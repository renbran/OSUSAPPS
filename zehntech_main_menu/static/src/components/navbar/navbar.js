/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        const root = this.menuService.getMenuAsTree("root").childrenTree;
        this.menuApp = root.find(app => app.xmlid === "zehntech_main_menu.main_menu_root");
    },
    onClickMenu() {
        this.onNavBarDropdownItemSelection(this.menuApp);
    },
});
