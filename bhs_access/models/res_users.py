# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging


_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # def write(self, vals):  # vals['groups_id'] = [(6, 0, [])]
    #     if self.env.context.get('bhs_access_management') and vals.get('groups_id') and vals.get('groups_id')[0][0] == 6:
    #         bhs_groups = self.env['res.groups'].search([('category_id', '=', self.env.ref('bhs_access.bhs_access_category').id)])
    #         group_ids = [grp_id for grp_id in vals.get('groups_id')[0][2] if grp_id in bhs_groups.ids] or []
    #         group_ids.append(self.env.ref('base.group_user').id)  # Add group_user so share & notification_type is not affected
    #         group_vals = [(6, 0, group_ids)]
    #         vals['groups_id'] = group_vals
    #     return super(ResUsers, self.sudo()).write(vals)

    def write(self, vals):  # vals['groups_id'] = [[3, id], [3, id], [4, id], ...]
        """
        Inherit write func of res.users to process if vals get groups_id
        Only process with bhs access management, keep old func with default view
        """

        bhs_groups_ids = self.env['res.groups'].search([
            ('category_id', '=', self.env.ref('bhs_access.bhs_access_category').id)
        ]).ids

        if self.env.context.get('bhs_access_management') and vals.get('groups_id'):
            user_bhs_group_ids = []
            for group in self.groups_id:  # tất cả group của user
                if group.category_id == self.env.ref('bhs_access.bhs_access_category'):
                    user_bhs_group_ids.append(group.id)  # tất cả group bhs cũ của user

            to_remove_bhs = []  # chứa những group bhs bị bỏ chọn
            to_add_bhs = []  # chứa những group bhs được thêm

            for item in vals['groups_id']:
                # những group bhs bị bỏ chọn
                if item[0] == 3 and item[1] in bhs_groups_ids:
                    to_remove_bhs.append(item[1])
                # những group bhs được thêm
                if item[0] == 4 and item[1] in bhs_groups_ids:
                    to_add_bhs.append(item[1])

            # những group cần truyền vào
            res_group_bhs = [g for g in (user_bhs_group_ids + to_add_bhs) if g not in to_remove_bhs]
            res_group_id = self.env['res.groups'].search([('id', 'in', res_group_bhs)]).trans_implied_ids.ids
            res_group_id += res_group_bhs

            vals['groups_id'] = [(6, 0, res_group_id)]
        return super(ResUsers, self.sudo()).write(vals)
