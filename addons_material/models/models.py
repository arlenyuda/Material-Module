from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Material(models.Model):
    _name = 'material.material'
    _description = 'Material'
    _sql_constraints = [
        ('unique_code', 'unique (code)', 'Code must have a unique name.'),
    ]

    name = fields.Char(string="Material Name", required=True)
    code = fields.Char(string="Material Code", required=True)
    material_type = fields.Selection(
        selection=[('fabric', 'Fabric'), ('jeans', 'Jeans'), ('cotton', 'Cotton')],
        string="Material Type", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", 
        default=lambda self: self.env.company.currency_id.id)
    buy_price = fields.Monetary(string="Material Buy Price", required=True)
    supplier_id = fields.Many2one(comodel_name="res.partner", string="Related Supplier", required=True)

    @api.constrains('buy_price')
    def check_buy_price(self):
        for record in self:
            if record.buy_price and record.buy_price < 100:
                raise ValidationError("Buy Price must be more than 100!")