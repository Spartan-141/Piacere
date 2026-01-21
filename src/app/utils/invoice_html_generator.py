from typing import List, Dict, Any, Union
from datetime import datetime

def generate_invoice_html(
    numero_factura: str,
    fecha: Union[str, datetime],
    cliente: str,
    forma_pago: str,
    total_usd: float,
    total_ves: float,
    items: List[Dict[str, Any]],
) -> str:
    """
    Genera el HTML de la factura con fondo blanco y formato profesional.
    """
    
    # Parsear fecha
    try:
        if isinstance(fecha, str):
            try:
                fecha_obj = datetime.fromisoformat(fecha.replace(" ", "T"))
                fecha_formatted = fecha_obj.strftime("%d/%m/%Y %I:%M %p")
            except ValueError:
                fecha_formatted = fecha
        elif isinstance(fecha, datetime):
            fecha_formatted = fecha.strftime("%d/%m/%Y %I:%M %p")
        else:
            fecha_formatted = str(fecha)
    except Exception:
        fecha_formatted = str(fecha)

    # Construir tabla de items
    items_html = []
    
    for item in items:
        if isinstance(item, (list, tuple)):
            producto = item[0] or "Producto"
            variante = item[1] if len(item) > 1 else ""
            cantidad = item[2] if len(item) > 2 else 0
            
            subtotal = item[4] if len(item) > 4 else 0.0
        elif isinstance(item, dict):
            producto = item.get("producto") or item.get("nombre") or "Producto"
            variante = item.get("variante") or item.get("descripcion") or ""
            cantidad = item.get("cantidad", 0)
            
            subtotal = item.get("subtotal", 0.0)
        else:
            continue

        try:
            cantidad = int(float(cantidad))
            
            subtotal = float(subtotal)
        except:
            pass

        nombre_completo = f"{producto}"
        if variante:
            nombre_completo += f" <br><span style='font-size:10pt;color:#555'>({variante})</span>"

        items_html.append(
            f"""
            <tr>
                <td style='padding: 6px 8px; border-bottom: 1px solid #eee;'>{nombre_completo}</td>
                <td style='padding: 6px 8px; text-align: center; border-bottom: 1px solid #eee;'>{cantidad}</td>
                <td style='padding: 6px 8px; text-align: right; border-bottom: 1px solid #eee;'>${subtotal:.2f}</td>
            </tr>
        """
        )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            /* Reset y fondo blanco total */
            body {{
                font-family: 'Courier New', monospace;
                background-color: #ffffff;
                margin: 0;
                padding: 10px;
                color: #000;
            }}
            .invoice-container {{
                max-width: 750px;
                margin: 0 auto;
                background-color: #ffffff;
                border: 1px solid #ccc; /* Borde más sutil */
                padding: 30px;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #000;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28pt;
                font-weight: bold;
            }}
            .header p {{
                margin: 3px 0;
                font-size: 11pt;
            }}
            .meta {{
                margin-bottom: 20px;
                padding: 10px 0;
            }}
            .meta-row {{
                margin: 4px 0;
                font-size: 11pt;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #f9f9f9;
                padding: 10px;
                text-align: left;
                border-bottom: 2px solid #000;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 10pt;
            }}
            .totals {{
                margin-top: 20px;
                border-top: 2px solid #000;
                padding-top: 10px;
            }}
            .total-row {{
                text-align: right;
                margin: 6px 0;
                font-size: 11pt;
            }}
            .total-row span:first-child {{
                margin-right: 20px;
                font-weight: bold;
            }}
            .total-row.grand {{
                font-size: 16pt;
                font-weight: bold;
                border-top: 1px double #000;
                padding-top: 8px;
                margin-top: 8px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px dashed #999;
                font-size: 10pt;
            }}
            @media print {{
                body {{ padding: 0; margin: 0; }}
                .invoice-container {{ border: none; width: 100%; max-width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <div class="header">
                <h1>PIACERE</h1>
                <p>Calle No definido</p>
                <p>Tel: No definido</p>
                <p style="margin-top: 12px; font-weight: bold; font-size: 14pt;">FACTURA DE VENTA</p>
            </div>
            
            <div class="meta">
                <div class="meta-row"><strong>Factura #:</strong> {numero_factura}</div>
                <div class="meta-row"><strong>Fecha:</strong> {fecha_formatted}</div>
                <div class="meta-row"><strong>Cliente:</strong> {cliente}</div>
                <div class="meta-row"><strong>Forma de Pago:</strong> {forma_pago}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Ventas</th>
                        <th style="text-align: center; width: 60px;">Cant.</th>
                        <th style="text-align: right; width: 100px;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(items_html)}
                </tbody>
            </table>
            
            <div class="totals">
                
                <div class="total-row grand">
                    <span>TOTAL USD:</span>
                    <span>${total_usd:.2f}</span>
                </div>
                <div class="total-row" style="font-size: 13pt; margin-top: 5px;">
                    <span>TOTAL Bs:</span>
                    <span>{total_ves:,.2f} Bs</span>
                </div>
            </div>
            
            <div class="footer">
                
            </div>
        </div>
    </body>
    </html>
    """
    return html