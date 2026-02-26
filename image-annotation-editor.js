(function () {
  const DEFAULT_STROKE = '#ff9100';
  const DEFAULT_TEXT_COLOR = '#ffffff';
  const TEXT_COLORS = {
    white: '#ffffff',
    black: '#000000',
    red: '#ff0000',
  };

  const state = {
    modal: null,
    stageContainer: null,
    saveBtn: null,
    closeBtn: null,
    toolButtons: {},
    stage: null,
    bgLayer: null,
    drawLayer: null,
    transformer: null,
    drawing: null,
    currentTool: 'select',
    selectedNode: null,
    history: [],
    historyIndex: -1,
    options: null,
    imageUrl: null,
    currentTextColor: DEFAULT_TEXT_COLOR,
  };

  function ensureModal() {
    if (state.modal) return;

    const modal = document.createElement('div');
    modal.id = 'note-image-editor-modal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);display:none;z-index:4000;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;';

    modal.innerHTML = `
      <div style="width:min(1600px, 96vw);height:min(95vh, 1200px);background:#1a1a1a;border:2px solid #444;border-radius:12px;display:flex;flex-direction:column;">
        <div style="padding:10px 14px;border-bottom:1px solid #333;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <strong id="note-image-editor-title" style="margin-right:12px;color:#fff;">Edycja zdjęcia</strong>
          <button data-tool="select" style="padding:6px 10px;">Select</button>
          <button data-tool="text" style="padding:6px 10px;">Text</button>
          <button data-tool="arrow" style="padding:6px 10px;">Arrow</button>
          <button data-tool="rect" style="padding:6px 10px;">Rect</button>
          <button data-tool="circle" style="padding:6px 10px;">Circle</button>
          <span style="width:1px;height:24px;background:#555;margin:0 4px;"></span>
          <span style="color:#888;font-size:0.8rem;">Kolor:</span>
          <button data-text-color="white" title="Biały" style="padding:4px 10px;background:#ffffff;color:#000;font-weight:bold;border:2px solid #2979ff;border-radius:6px;">A</button>
          <button data-text-color="black" title="Czarny" style="padding:4px 10px;background:#000000;color:#fff;font-weight:bold;border:2px solid #555;border-radius:6px;">A</button>
          <button data-text-color="red" title="Czerwony" style="padding:4px 10px;background:#ff0000;color:#fff;font-weight:bold;border:2px solid #555;border-radius:6px;">A</button>
          <span style="width:1px;height:24px;background:#555;margin:0 4px;"></span>
          <button id="note-image-editor-delete" style="padding:6px 10px;background:#442222;color:#fff;">Delete</button>
          <button id="note-image-editor-undo" style="padding:6px 10px;">Undo</button>
          <div style="margin-left:auto;display:flex;gap:8px;">
            <button id="note-image-editor-close" style="padding:6px 12px;">Zamknij</button>
            <button id="note-image-editor-save" style="padding:6px 12px;background:#00e676;color:#000;font-weight:bold;">Zapisz adnotacje</button>
          </div>
        </div>
        <div id="note-image-editor-stage" style="flex:1;min-height:0;overflow:auto;background:#111;">
      </div>
    `;

    document.body.appendChild(modal);
    state.modal = modal;
    state.stageContainer = modal.querySelector('#note-image-editor-stage');
    state.saveBtn = modal.querySelector('#note-image-editor-save');
    state.closeBtn = modal.querySelector('#note-image-editor-close');

    modal.querySelectorAll('[data-tool]').forEach((btn) => {
      state.toolButtons[btn.dataset.tool] = btn;
      btn.addEventListener('click', () => setTool(btn.dataset.tool));
    });

    modal.querySelector('#note-image-editor-delete').addEventListener('click', () => {
      if (state.selectedNode) {
        state.selectedNode.destroy();
        clearSelection();
        pushHistory();
        state.drawLayer.draw();
      }
    });

    modal.querySelector('#note-image-editor-undo').addEventListener('click', undo);
    state.saveBtn.addEventListener('click', saveAndClose);
    state.closeBtn.addEventListener('click', close);

    // Color picker buttons
    modal.querySelectorAll('[data-text-color]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const colorName = btn.dataset.textColor;
        state.currentTextColor = TEXT_COLORS[colorName] || DEFAULT_TEXT_COLOR;
        // Update border highlight
        modal.querySelectorAll('[data-text-color]').forEach((b) => {
          b.style.border = '2px solid #555';
        });
        btn.style.border = '2px solid #2979ff';
      });
    });
  }

  function setTool(toolName) {
    state.currentTool = toolName;
    Object.entries(state.toolButtons).forEach(([key, btn]) => {
      btn.style.background = key === toolName ? '#2979ff' : '#2b2b2b';
      btn.style.color = '#fff';
      btn.style.border = '1px solid #555';
      btn.style.borderRadius = '6px';
    });
    if (toolName !== 'select') clearSelection();
  }

  function close() {
    if (state.imageUrl && state.imageUrl.startsWith('blob:')) {
      URL.revokeObjectURL(state.imageUrl);
    }
    if (state.stage) {
      state.stage.destroy();
      state.stage = null;
    }
    state.bgLayer = null;
    state.drawLayer = null;
    state.transformer = null;
    state.selectedNode = null;
    state.history = [];
    state.historyIndex = -1;
    state.options = null;
    state.imageUrl = null;
    if (state.modal) state.modal.style.display = 'none';
  }

  function clearSelection() {
    state.selectedNode = null;
    if (state.transformer) {
      state.transformer.nodes([]);
      state.drawLayer.draw();
    }
  }

  function selectNode(node) {
    state.selectedNode = node;
    if (state.transformer) {
      state.transformer.nodes([node]);
      state.drawLayer.draw();
    }
  }

  function normalizePoint(value, max) {
    if (!max) return 0;
    return Number((value / max).toFixed(6));
  }

  function denormalizePoint(value, max) {
    return Number((value * max).toFixed(3));
  }

  function serializeAnnotations() {
    if (!state.stage || !state.drawLayer) return { version: 1, objects: [] };
    const width = state.stage.width();
    const height = state.stage.height();
    const objects = [];

    state.drawLayer.getChildren().forEach((node) => {
      if (!node || node === state.transformer) return;
      const type = node.getClassName();
      if (type === 'Rect') {
        objects.push({
          type: 'rect',
          x: normalizePoint(node.x(), width),
          y: normalizePoint(node.y(), height),
          width: normalizePoint(node.width() * node.scaleX(), width),
          height: normalizePoint(node.height() * node.scaleY(), height),
          stroke: node.stroke() || DEFAULT_STROKE,
          strokeWidth: node.strokeWidth() || 3,
        });
      } else if (type === 'Circle') {
        objects.push({
          type: 'circle',
          x: normalizePoint(node.x(), width),
          y: normalizePoint(node.y(), height),
          radius: normalizePoint(node.radius() * Math.max(node.scaleX(), node.scaleY()), width),
          stroke: node.stroke() || DEFAULT_STROKE,
          strokeWidth: node.strokeWidth() || 3,
        });
      } else if (type === 'Arrow') {
        const pts = node.points();
        objects.push({
          type: 'arrow',
          points: pts.map((p, i) => (i % 2 === 0 ? normalizePoint(p, width) : normalizePoint(p, height))),
          stroke: node.stroke() || DEFAULT_STROKE,
          strokeWidth: node.strokeWidth() || 3,
        });
      } else if (type === 'Text') {
        objects.push({
          type: 'text',
          x: normalizePoint(node.x(), width),
          y: normalizePoint(node.y(), height),
          text: node.text() || '',
          fontSize: normalizePoint(node.fontSize(), width),
          fill: node.fill() || DEFAULT_TEXT_COLOR,
        });
      }
    });

    return { version: 1, objects };
  }

  function applyAnnotations(annotations) {
    if (!state.drawLayer || !state.stage) return;
    const width = state.stage.width();
    const height = state.stage.height();

    state.drawLayer.destroyChildren();

    const objects = (annotations && Array.isArray(annotations.objects)) ? annotations.objects : [];
    objects.forEach((obj) => {
      if (!obj || !obj.type) return;
      if (obj.type === 'rect') {
        state.drawLayer.add(new Konva.Rect({
          x: denormalizePoint(obj.x || 0, width),
          y: denormalizePoint(obj.y || 0, height),
          width: denormalizePoint(obj.width || 0.2, width),
          height: denormalizePoint(obj.height || 0.15, height),
          stroke: obj.stroke || DEFAULT_STROKE,
          strokeWidth: obj.strokeWidth || 3,
          draggable: true,
        }));
      } else if (obj.type === 'circle') {
        state.drawLayer.add(new Konva.Circle({
          x: denormalizePoint(obj.x || 0, width),
          y: denormalizePoint(obj.y || 0, height),
          radius: denormalizePoint(obj.radius || 0.07, width),
          stroke: obj.stroke || DEFAULT_STROKE,
          strokeWidth: obj.strokeWidth || 3,
          draggable: true,
        }));
      } else if (obj.type === 'arrow') {
        const pts = Array.isArray(obj.points) ? obj.points : [0.1, 0.1, 0.3, 0.3];
        const denorm = pts.map((p, i) => (i % 2 === 0 ? denormalizePoint(p, width) : denormalizePoint(p, height)));
        state.drawLayer.add(new Konva.Arrow({
          points: denorm,
          stroke: obj.stroke || DEFAULT_STROKE,
          fill: obj.stroke || DEFAULT_STROKE,
          strokeWidth: obj.strokeWidth || 3,
          pointerLength: 10,
          pointerWidth: 10,
          draggable: true,
        }));
      } else if (obj.type === 'text') {
        state.drawLayer.add(new Konva.Text({
          x: denormalizePoint(obj.x || 0, width),
          y: denormalizePoint(obj.y || 0, height),
          text: obj.text || '',
          fontSize: Math.max(14, denormalizePoint(obj.fontSize || 0.02, width)),
          fill: obj.fill || DEFAULT_TEXT_COLOR,
          draggable: true,
          fontStyle: 'bold',
        }));
      }
    });

    state.transformer = new Konva.Transformer({
      rotateEnabled: false,
      ignoreStroke: true,
      borderStroke: '#2979ff',
      anchorFill: '#2979ff',
      anchorStroke: '#fff',
      anchorSize: 8,
    });
    state.drawLayer.add(state.transformer);
    state.drawLayer.draw();
  }

  function pushHistory() {
    const snapshot = JSON.stringify(serializeAnnotations());
    if (state.historyIndex >= 0 && state.history[state.historyIndex] === snapshot) return;
    state.history = state.history.slice(0, state.historyIndex + 1);
    state.history.push(snapshot);
    state.historyIndex = state.history.length - 1;
  }

  function undo() {
    if (state.historyIndex <= 0) return;
    state.historyIndex -= 1;
    const snapshot = JSON.parse(state.history[state.historyIndex]);
    applyAnnotations(snapshot);
    state.drawLayer.draw();
  }

  function bindStageHandlers() {
    let startPoint = null;

    state.stage.on('mousedown touchstart', (evt) => {
      const target = evt.target;
      const pointer = state.stage.getPointerPosition();
      if (!pointer) return;

      if (state.currentTool === 'select') {
        if (target && target !== state.stage && target !== state.transformer) {
          selectNode(target);
        } else {
          clearSelection();
        }
        return;
      }

      if (state.currentTool === 'text') {
        const value = prompt('Wpisz tekst adnotacji:');
        if (!value) return;
        const textNode = new Konva.Text({
          x: pointer.x,
          y: pointer.y,
          text: value,
          fill: state.currentTextColor,
          fontSize: 22,
          fontStyle: 'bold',
          draggable: true,
        });
        state.drawLayer.add(textNode);
        state.drawLayer.draw();
        pushHistory();
        return;
      }

      startPoint = { x: pointer.x, y: pointer.y };
      if (state.currentTool === 'rect') {
        state.drawing = new Konva.Rect({
          x: pointer.x,
          y: pointer.y,
          width: 1,
          height: 1,
          stroke: DEFAULT_STROKE,
          strokeWidth: 3,
          draggable: true,
        });
      } else if (state.currentTool === 'circle') {
        state.drawing = new Konva.Circle({
          x: pointer.x,
          y: pointer.y,
          radius: 1,
          stroke: DEFAULT_STROKE,
          strokeWidth: 3,
          draggable: true,
        });
      } else if (state.currentTool === 'arrow') {
        state.drawing = new Konva.Arrow({
          points: [pointer.x, pointer.y, pointer.x + 1, pointer.y + 1],
          stroke: DEFAULT_STROKE,
          fill: DEFAULT_STROKE,
          strokeWidth: 3,
          pointerLength: 10,
          pointerWidth: 10,
          draggable: true,
        });
      }

      if (state.drawing) {
        state.drawLayer.add(state.drawing);
        state.drawLayer.draw();
      }
    });

    state.stage.on('mousemove touchmove', () => {
      if (!state.drawing || !startPoint) return;
      const pointer = state.stage.getPointerPosition();
      if (!pointer) return;

      if (state.currentTool === 'rect') {
        state.drawing.width(pointer.x - startPoint.x);
        state.drawing.height(pointer.y - startPoint.y);
      } else if (state.currentTool === 'circle') {
        const dx = pointer.x - startPoint.x;
        const dy = pointer.y - startPoint.y;
        state.drawing.radius(Math.sqrt(dx * dx + dy * dy));
      } else if (state.currentTool === 'arrow') {
        state.drawing.points([startPoint.x, startPoint.y, pointer.x, pointer.y]);
      }
      state.drawLayer.batchDraw();
    });

    state.stage.on('mouseup touchend', () => {
      if (state.drawing) {
        pushHistory();
      }
      state.drawing = null;
      startPoint = null;
    });

    state.drawLayer.on('click tap', (evt) => {
      if (state.currentTool !== 'select') return;
      const node = evt.target;
      if (node && node !== state.drawLayer && node !== state.transformer) {
        selectNode(node);
      }
    });

    state.drawLayer.on('dragend transformend', () => {
      pushHistory();
    });
  }

  async function saveAndClose() {
    if (!state.options || typeof state.options.onSave !== 'function') {
      close();
      return;
    }
    const payload = serializeAnnotations();
    state.saveBtn.disabled = true;
    try {
      await state.options.onSave(payload);
      close();
    } catch (err) {
      alert(`Nie udalo sie zapisac adnotacji: ${err.message || err}`);
    } finally {
      if (state.saveBtn) state.saveBtn.disabled = false;
    }
  }

  async function open(options) {
    ensureModal();
    if (!window.Konva) {
      alert('Brak biblioteki Konva.');
      return;
    }

    state.options = options || {};
    const titleEl = state.modal.querySelector('#note-image-editor-title');
    titleEl.textContent = state.options.title || 'Edycja zdjęcia';

    const imageSource = state.options.imageSource;
    if (!imageSource) {
      alert('Brak źródła obrazu');
      return;
    }

    if (state.imageUrl && state.imageUrl.startsWith('blob:')) {
      URL.revokeObjectURL(state.imageUrl);
    }
    state.imageUrl = imageSource instanceof Blob ? URL.createObjectURL(imageSource) : String(imageSource);

    const img = await new Promise((resolve, reject) => {
      const image = new window.Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error('Nie udało się załadować obrazu'));
      image.src = state.imageUrl;
    });

    const containerRect = state.stageContainer.getBoundingClientRect();
    const maxW = Math.max(320, containerRect.width - 20);
    const maxH = Math.max(240, containerRect.height - 20);
    const ratio = Math.min(maxW / img.width, maxH / img.height, 4);
    const stageWidth = Math.max(320, Math.floor(img.width * ratio));
    const stageHeight = Math.max(240, Math.floor(img.height * ratio));

    state.stageContainer.innerHTML = '';
    state.stage = new Konva.Stage({
      container: state.stageContainer,
      width: stageWidth,
      height: stageHeight,
    });

    state.bgLayer = new Konva.Layer();
    state.drawLayer = new Konva.Layer();

    const bgImage = new Konva.Image({
      image: img,
      x: 0,
      y: 0,
      width: stageWidth,
      height: stageHeight,
      listening: false,
    });
    state.bgLayer.add(bgImage);

    state.stage.add(state.bgLayer);
    state.stage.add(state.drawLayer);

    applyAnnotations(state.options.annotations || { version: 1, objects: [] });
    bindStageHandlers();
    setTool('select');
    pushHistory();

    state.modal.style.display = 'flex';
  }

  async function compressImageFile(file, options) {
    const opts = options || {};
    const maxDimension = Number(opts.maxDimension || 1600);
    const quality = Number(opts.quality || 0.82);

    const bitmap = await createImageBitmap(file);
    const ratio = Math.min(1, maxDimension / Math.max(bitmap.width, bitmap.height));
    const width = Math.max(1, Math.round(bitmap.width * ratio));
    const height = Math.max(1, Math.round(bitmap.height * ratio));

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: false });
    ctx.drawImage(bitmap, 0, 0, width, height);
    bitmap.close();

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/webp', quality));
    if (!blob) throw new Error('Kompresja obrazu nie powiodla sie');
    return blob;
  }

  window.NoteImageEditor = {
    open,
    close,
    compressImageFile,
  };
})();
