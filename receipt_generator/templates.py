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
        y_offset = self.padding

        # Store name
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width // 2, y_offset),
            content=store_name,
            font_size=20,
            bold=True,
            alignment=Alignment.CENTER
        ))
        y_offset += 30

        # Address lines
        for line in address:
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width // 2, y_offset),
                content=line,
                font_size=10,
                alignment=Alignment.CENTER
            ))
            y_offset += 15

        # Phone
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width // 2, y_offset),
            content=phone,
            font_size=10,
            alignment=Alignment.CENTER
        ))
        y_offset += 25

        # Separator line
        self.elements.append(ReceiptElement(
            type=ElementType.LINE,
            position=(self.padding, y_offset),
            width=self.width - 2 * self.padding
        ))

        return y_offset + 10

    def add_items(self, items: List[Dict], start_y: int):
        y_offset = start_y

        for item in items:
            # Item name
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.padding, y_offset),
                content=item['name'],
                font_size=11,
                alignment=Alignment.LEFT
            ))

            # Total price on the right
            self.elements.append(ReceiptElement(
                type=ElementType.TEXT,
                position=(self.width - self.padding, y_offset),
                content=f"${item['total']:.2f}",
                font_size=11,
                alignment=Alignment.RIGHT
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
        y_offset = start_y

        # Transaction details
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width // 2, y_offset),
            content=f"Transaction: {transaction_id}",
            font_size=9,
            alignment=Alignment.CENTER
        ))
        y_offset += 15

        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width // 2, y_offset),
            content=date_time,
            font_size=9,
            alignment=Alignment.CENTER
        ))
        y_offset += 25

        # Thank you message
        self.elements.append(ReceiptElement(
            type=ElementType.TEXT,
            position=(self.width // 2, y_offset),
            content="Thank you for your purchase!",
            font_size=11,
            alignment=Alignment.CENTER
        ))

        return y_offset + 20

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