from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Material(models.Model):
    _name = 'material.material'
    _description = 'Material'
    _sql_constraints = [
        ('unique_code', 'unique (code)', 'Code must have a unique name.'),
    ]

    name = fields.Char(string="Material Name", required=True)
    code = fields.Char(string="Material Code", required=True, copy=False, index=True)
    material_type = fields.Selection(
        selection=[('fabric', 'Fabric'), ('jeans', 'Jeans'), ('cotton', 'Cotton')],
        string="Material Type", required=True, index=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", 
        default=lambda self: self.env.company.currency_id.id)
    buy_price = fields.Monetary(string="Material Buy Price", required=True)
    supplier_id = fields.Many2one(comodel_name="res.partner", string="Related Supplier", required=True)

    @api.constrains('buy_price')
    def check_buy_price(self):
        for record in self:
            if record.buy_price and record.buy_price < 100:
                raise ValidationError("Buy Price must be more than 100!")

    def copy(self, default=None):
        """
        Ensure unique 'code' when duplicating a material record.

        Appends '_copy', '_copy_1', etc., to the original code to avoid unique constraint errors.
        Raises ValidationError if the original code is empty.
        """
        self.ensure_one()
        if not self.code:
            raise ValidationError("Cannot duplicate a material with an empty code.")

        base_code = self.code + '_copy'
        new_code = base_code
        count = 1
        while self.env['material.material'].sudo().search_count([('code', '=', new_code)]):
            new_code = f"{base_code}_{count}"
            count += 1

        default = dict(default or {})
        default['code'] = new_code
        return super(Material, self).copy(default)