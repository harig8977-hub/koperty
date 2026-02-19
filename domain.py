from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, List

class EnvelopeStatus(Enum):
    """Definiuje dozwolone stany koperty (Maszyna Stanów)."""
    MAGAZYN = "MAGAZYN"
    W_TRANSPORCIE_OUT = "W_TRANSPORCIE_OUT"  # Na wózku wydawczym
    SHOP_FLOOR = "SHOP_FLOOR"                # Na hali (wyjęte z wózka lub zwolnione z maszyny)
    W_PRODUKCJI = "W_PRODUKCJI"              # Na maszynie
    CART_RET_05 = "CART-RET-05"              # Na wózku zwrotnym (specyficzny status dla tego przepływu)
    W_TRANSPORCIE_RET = "W_TRANSPORCIE_RET"  # Ogólny transport zwrotny
    USZKODZONA = "USZKODZONA"
    WYCOFANA = "WYCOFANA"

class CreationReason(Enum):
    """Powód nadania numeru dodatkowego."""
    NEW = "NEW"
    DUPLICATE = "DUPLICATE"
    VERSION_CHANGE = "VERSION_CHANGE"

class HolderType(Enum):
    """Typ posiadacza koperty."""
    WAREHOUSE = "WAREHOUSE"
    CART_OUT = "CART_OUT"
    CART_IN = "CART_IN"      # Wózek przychodzący (zwrotny)
    CART_RET = "CART_RET"    # (Deprecated - używać CART_IN lub specyficznych ID)
    FLOOR = "FLOOR"          # Podłoga/Hala (brak konkretnego przypisania)
    MACHINE = "MACHINE"

# Dozwolone przejścia stanów
ALLOWED_TRANSITIONS: Dict[EnvelopeStatus, List[EnvelopeStatus]] = {
    EnvelopeStatus.MAGAZYN: [EnvelopeStatus.W_TRANSPORCIE_OUT, EnvelopeStatus.SHOP_FLOOR, EnvelopeStatus.WYCOFANA],
    EnvelopeStatus.W_TRANSPORCIE_OUT: [EnvelopeStatus.SHOP_FLOOR, EnvelopeStatus.MAGAZYN], 
    EnvelopeStatus.SHOP_FLOOR: [EnvelopeStatus.W_PRODUKCJI, EnvelopeStatus.CART_RET_05, EnvelopeStatus.W_TRANSPORCIE_RET, EnvelopeStatus.MAGAZYN],
    EnvelopeStatus.W_PRODUKCJI: [EnvelopeStatus.SHOP_FLOOR, EnvelopeStatus.CART_RET_05, EnvelopeStatus.W_TRANSPORCIE_RET, EnvelopeStatus.USZKODZONA],
    EnvelopeStatus.CART_RET_05: [EnvelopeStatus.MAGAZYN, EnvelopeStatus.SHOP_FLOOR], # Możliwość cofnięcia na halę
    EnvelopeStatus.W_TRANSPORCIE_RET: [EnvelopeStatus.MAGAZYN],
    EnvelopeStatus.USZKODZONA: [EnvelopeStatus.WYCOFANA, EnvelopeStatus.MAGAZYN], 
    # WYCOFANA to stan końcowy
}

@dataclass
class Envelope:
    """
    Fizyczna reprezentacja jednej koperty w systemie.
    Klucz główny: base_id + product_version + additional_number
    """
    rcs_id: str
    product_version: str
    additional_number: int
    
    status: EnvelopeStatus
    current_holder_id: str
    current_holder_type: HolderType
    
    creation_reason: CreationReason
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Nowe pole: Dział w magazynie (opcjonalne)
    warehouse_section: Optional[str] = None

    def __post_init__(self):
        """Walidacja po inicjalizacji."""
        if self.additional_number < 1:
            raise ValueError(
                f"additional_number musi być >= 1, otrzymano: {self.additional_number}"
            )

    @property
    def unique_key(self) -> str:
        """Zwraca unikalny klucz uwzględniający wersję."""
        return f"{self.rcs_id}#{self.product_version}#{self.additional_number}"
        
    def set_location(self, section_letter: str):
        """Umożliwia przypisanie lub zmianę działu w magazynie."""
        if not section_letter.isalpha() or len(section_letter) != 1:
            raise ValueError("Dział magazynu musi być pojedynczą literą.")
        
        self.warehouse_section = section_letter.upper()
        self.updated_at = datetime.now(timezone.utc)

    def can_transition_to(self, new_status: EnvelopeStatus) -> bool:
        """Sprawdza, czy przejście jest dozwolone."""
        return new_status in ALLOWED_TRANSITIONS.get(self.status, [])

    def transition_to(
        self, 
        new_status: EnvelopeStatus, 
        new_holder_id: str,
        new_holder_type: HolderType
    ):
        """Zmienia status z walidacją."""
        if not self.can_transition_to(new_status):
            # Logika biznesowa - rzucamy wyjątek, ale w realnej apce można to logować
            raise ValueError(
                f"Niedozwolone przejście: {self.status.value} -> {new_status.value}"
            )
        self.status = new_status
        self.current_holder_id = new_holder_id
        self.current_holder_type = new_holder_type
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        return (
            f"<Envelope {self.unique_key} | "
            f"Status: {self.status.value} | "
            f"Holder: {self.current_holder_type.value}:{self.current_holder_id}>"
        )


@dataclass
class EnvelopeEvent:
    """Zdarzenie w historii koperty (audit trail)."""
    envelope_key: str
    timestamp: datetime
    user_id: str
    from_status: EnvelopeStatus
    to_status: EnvelopeStatus
    from_holder: str
    to_holder: str
    device_id: Optional[str] = None
    comment: Optional[str] = None

@dataclass
class MachineSetupNote:
    """
    Notatka-szablon stworzona przez operatora dla innych operatorów.
    Pomaga bazowo ustawić maszynę pod dany produkt.
    """
    machine_id: str          # Np. "S1" - klucz partycjonowania (widoczne tylko tu)
    product_id: str          # Np. "PROD-001" - klucz wyszukiwania
    operator_name: str       # Autor notatki
    
    # Parametry techniczne (stringi, by zachować elastyczność np. "2.5mm" lub "ok. 3mm")
    glue_length: str         # Długość kleju
    machine_speed: str       # Prędkość maszyny
    width: str               # Szerokość koperty/taśmy
    
    description: str         # Dowolna uwaga dodatkowa
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return (f"<SetupNote {self.product_id} @ {self.machine_id} | Author: {self.operator_name}>")
