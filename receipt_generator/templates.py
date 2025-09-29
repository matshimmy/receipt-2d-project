from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class ElementType(Enum):
    TEXT = "text"
    LINE = "line"
    IMAGE = "image"
    BARCODE = "barcode"


class Alignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class ReceiptElement:
    type: ElementType
    position: Tuple[int, int]
    content: str = ""
    font_size: int = 12
    bold: bool = False
    alignment: Alignment = Alignment.LEFT
    width: Optional[int] = None
    element_type: str = "text"  # For font selection (e.g., "store_name", "item_price", etc.)


@dataclass
class ReceiptTemplate:
    name: str
    width: int = 300
    height: int = 600
    padding: int = 20
    background_color: Tuple[int, int, int] = (255, 255, 255)
    text_color: Tuple[int, int, int] = (0, 0, 0)
    font_family: str = "Arial"
    elements: List[ReceiptElement] = field(default_factory=list)

    def add_header(self, store_name: str, address: List[str], phone: str):
        import random
        y_offset = self.padding

        # Helper function to truncate text if too long
        def truncate_text(text, max_chars):
            if len(text) > max_chars:
                return text[:max_chars-3] + "..."
            return text

        # Randomly choose header style
        header_style = random.choice(["centered", "minimal", "detailed", "compact"])

        if header_style == "minimal":
            # Just store name, no address/phone
            store_display = truncate_text(store_name.upper(), 28)
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=store_display,
                font_size=14,  # Reduced from 16
                bold=True,
                alignment=Alignment.LEFT,
                element_type="store_name"
            ))
            y_offset += 28

        elif header_style == "compact":
            # Store name and minimal info
            store_display = truncate_text(store_name, 25)
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=store_display,
                font_size=15,  # Reduced from 18
                bold=True,
                alignment=Alignment.CENTER,
                element_type="store_name"
            ))
            y_offset += 28  # Increased spacing

            # Just city/state, no full address (50% chance)
            if random.random() < 0.5 and len(address) > 1:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=truncate_text(address[-1], 40),  # City, State ZIP
                    font_size=9,
                    alignment=Alignment.CENTER,
                    element_type="address"
                ))
                y_offset += 22

        elif header_style == "detailed":
            # Full details
            store_display = truncate_text(store_name, 22)
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=store_display,
                font_size=16,  # Reduced from 20
                bold=True,
                alignment=Alignment.CENTER,
                element_type="store_name"
            ))
            y_offset += 32  # Increased spacing

            # All address lines
            for line in address:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=truncate_text(line, 38),
                    font_size=10,
                    alignment=Alignment.CENTER,
                    element_type="address"
                ))
                y_offset += 17  # Increased spacing

            # Phone
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=truncate_text(phone, 35),
                font_size=10,
                alignment=Alignment.CENTER,
                element_type="phone"
            ))
            y_offset += 22  # Increased spacing

            # Sometimes add store number or register info
            if random.random() < 0.3:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=f"Store #{random.randint(100, 999)} Reg #{random.randint(1, 9)}",
                    font_size=8,
                    alignment=Alignment.CENTER
                ))
                y_offset += 18  # Increased spacing

        else:  # centered (standard)
            # Store name
            store_display = truncate_text(store_name, 22)
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=store_display,
                font_size=16,  # Reduced from 20
                bold=True,
                alignment=Alignment.CENTER,
                element_type="store_name"
            ))
            y_offset += 32  # Increased spacing

            # Sometimes skip address (20% chance)
            if random.random() < 0.8:
                # Address lines (sometimes just one line)
                if random.random() < 0.6:
                    for line in address:
                        self.elements.append(ReceiptElement(
                            type=ElementType.TEXT,
                            position=(self.width // 2, y_offset),
                            content=line,
                            font_size=10,
                            alignment=Alignment.CENTER,
                            element_type="address"
                        ))
                        y_offset += 15
                else:
                    # Combined address on one line
                    if len(address) > 0:
                        combined = address[0] if len(address) == 1 else f"{address[0]}, {address[1]}"
                        self.elements.append(ReceiptElement(
                            type=ElementType.TEXT,
                            position=(self.width // 2, y_offset),
                            content=truncate_text(combined, 42),
                            font_size=9,
                            alignment=Alignment.CENTER,
                            element_type="address"
                        ))
                        y_offset += 15

            # Phone (70% chance)
            if random.random() < 0.7:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=phone,
                    font_size=10,
                    alignment=Alignment.CENTER,
                    element_type="phone"
                ))
                y_offset += 20

        y_offset += 5

        # Separator line (80% chance)
        if random.random() < 0.8:
            self.elements.append(ReceiptElement(
                type=ElementType.LINE,
                position=(self.padding, y_offset),
                width=self.width - 2 * self.padding
            ))
            y_offset += 10
        else:
            y_offset += 5

        return y_offset

    def add_items(self, items: List[Dict], start_y: int):
        y_offset = start_y

        for item in items:
            # Item name
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=item['name'],
                font_size=11,
                alignment=Alignment.LEFT,
                element_type="item_name"
            ))

            # Total price on the right
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width - self.padding, y_offset),
                content=f"${item['total']:.2f}",
                font_size=11,
                alignment=Alignment.RIGHT,
                element_type="item_price"
            ))

            # Quantity details on next line if needed
            if item.get('quantity', 1) > 1:
                y_offset += 15
                qty_price = f"  {item['quantity']} x ${item['unit_price']:.2f}"
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.padding + 10, y_offset),
                    content=qty_price,
                    font_size=9,
                    alignment=Alignment.LEFT
                ))
                y_offset += 15
            else:
                y_offset += 20

        return y_offset

    def add_totals(self, subtotal: float, tax: float, total: float, start_y: int):
        y_offset = start_y

        # Separator line
        self.elements.append(ReceiptElement(
            type=ElementType.LINE,
            position=(self.padding, y_offset),
            width=self.width - 2 * self.padding
        ))
        y_offset += 15

        # Subtotal
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.padding, y_offset),
            content="Subtotal:",
            font_size=11
        ))
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width - self.padding, y_offset),
            content=f"${subtotal:.2f}",
            font_size=11,
            alignment=Alignment.RIGHT
        ))
        y_offset += 20

        # Tax
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.padding, y_offset),
            content="Tax:",
            font_size=11
        ))
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width - self.padding, y_offset),
            content=f"${tax:.2f}",
            font_size=11,
            alignment=Alignment.RIGHT
        ))
        y_offset += 20

        # Total
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.padding, y_offset),
            content="TOTAL:",
            font_size=14,
            bold=True
        ))
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width - self.padding, y_offset),
            content=f"${total:.2f}",
            font_size=14,
            bold=True,
            alignment=Alignment.RIGHT
        ))

        return y_offset + 30

    def add_footer(self, transaction_id: str, date_time: str, start_y: int):
        import random
        y_offset = start_y

        # Randomly choose footer style
        footer_style = random.choice(["minimal", "standard", "detailed", "compact", "spread"])

        if footer_style == "minimal":
            # Just date/time, no transaction ID or thank you
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=date_time,
                font_size=8,
                alignment=Alignment.LEFT,
                element_type="timestamp"
            ))
            return y_offset + 15

        elif footer_style == "compact":
            # Transaction ID and date on same line
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=f"#{transaction_id[:8]}",
                font_size=8,
                alignment=Alignment.LEFT,
                element_type="transaction"
            ))
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width - self.padding, y_offset),
                content=date_time.split()[0],  # Just date, no time
                font_size=8,
                alignment=Alignment.RIGHT,
                element_type="timestamp"
            ))
            return y_offset + 20

        elif footer_style == "spread":
            # Spread elements across width
            # Date on left
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=date_time,
                font_size=9,
                alignment=Alignment.LEFT,
                element_type="timestamp"
            ))

            # Transaction in middle (sometimes)
            if random.random() < 0.6:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=f"TRN: {transaction_id[:6]}",
                    font_size=8,
                    alignment=Alignment.CENTER,
                    element_type="transaction"
                ))

            y_offset += 20

            # Random thank you (40% chance)
            if random.random() < 0.4:
                thank_you_msgs = [
                    "Thank You",
                    "Come Again",
                    "Have a Great Day",
                    "Thanks!",
                    "Visit Again Soon"
                ]
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=random.choice(thank_you_msgs),
                    font_size=10,
                    alignment=Alignment.CENTER,
                    element_type="thank_you"
                ))
                y_offset += 15

            return y_offset

        elif footer_style == "detailed":
            # More detailed footer with various elements

            # Transaction ID (70% chance)
            if random.random() < 0.7:
                tx_formats = [
                    f"Transaction: {transaction_id}",
                    f"Trans #{transaction_id}",
                    f"REF: {transaction_id[:10]}",
                    f"{transaction_id}"
                ]
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=random.choice(tx_formats),
                    font_size=9,
                    alignment=Alignment.CENTER,
                    element_type="transaction"
                ))
                y_offset += 15

            # Date/time (different formats)
            date_formats = [
                date_time,
                date_time.split()[0] + " " + date_time.split()[1],
                date_time.replace(" ", "  "),
            ]
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=random.choice(date_formats),
                font_size=9,
                alignment=Alignment.CENTER,
                element_type="timestamp"
            ))
            y_offset += 20

            # Additional elements (randomly included)
            if random.random() < 0.3:
                # Cashier info
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.padding, y_offset),
                    content=f"Cashier: {random.choice(['JOHN', 'MARY', 'ALEX', 'SAM', '#042'])}",
                    font_size=8,
                    alignment=Alignment.LEFT
                ))
                y_offset += 15

            if random.random() < 0.5:
                # Thank you message
                thank_you_msgs = [
                    "Thank you for your purchase!",
                    "Thanks for shopping with us",
                    "We appreciate your business",
                    "Thank You!",
                    "Have a nice day!"
                ]
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=random.choice(thank_you_msgs),
                    font_size=11,
                    alignment=Alignment.CENTER,
                    element_type="thank_you"
                ))
                y_offset += 20

            return y_offset

        else:  # standard
            # Traditional receipt footer

            # Sometimes no transaction ID (30% chance)
            if random.random() < 0.7:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content=f"Transaction: {transaction_id}",
                    font_size=9,
                    alignment=Alignment.CENTER,
                    element_type="transaction"
                ))
                y_offset += 15

            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=date_time,
                font_size=9,
                alignment=Alignment.CENTER,
                element_type="timestamp"
            ))
            y_offset += 20

            # Thank you message (60% chance)
            if random.random() < 0.6:
                self.elements.append(ReceiptElement(
                    type=ElementType.TEXT,
                    position=(self.width // 2, y_offset),
                    content="Thank you for your purchase!",
                    font_size=11,
                    alignment=Alignment.CENTER,
                    element_type="thank_you"
                ))
                y_offset += 20

            return y_offset

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'elements': [
                {
                    'type': elem.type.value,
                    'position': elem.position,
                    'content': elem.content,
                    'font_size': elem.font_size,
                    'bold': elem.bold,
                    'alignment': elem.alignment.value
                } for elem in self.elements
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReceiptTemplate':
        template = cls(
            name=data['name'],
            width=data.get('width', 300),
            height=data.get('height', 600)
        )

        for elem_data in data.get('elements', []):
            template.elements.append(ReceiptElement(
                type=ElementType(elem_data['type']),
                position=tuple(elem_data['position']),
                content=elem_data.get('content', ''),
                font_size=elem_data.get('font_size', 12),
                bold=elem_data.get('bold', False),
                alignment=Alignment(elem_data.get('alignment', 'left'))
            ))

        return template


class TemplateLibrary:
    @staticmethod
    def grocery_store() -> ReceiptTemplate:
        template = ReceiptTemplate(name="Grocery Store", width=350, height=800)
        template.font_family = "Courier"
        return template

    @staticmethod
    def restaurant() -> ReceiptTemplate:
        template = ReceiptTemplate(name="Restaurant", width=300, height=700)
        template.font_family = "Arial"
        return template

    @staticmethod
    def retail_store() -> ReceiptTemplate:
        template = ReceiptTemplate(name="Retail Store", width=320, height=750)
        template.font_family = "Helvetica"
        return template