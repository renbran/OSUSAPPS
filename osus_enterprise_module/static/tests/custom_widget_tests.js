/** @odoo-module **/
import { getFixture, mount } from "@web/../tests/helpers/utils";
import { CustomWidget } from "@osus_enterprise_module/js/components/custom_widget";

QUnit.module("OSUS Enterprise Module", (hooks) => {
  let target;
  hooks.beforeEach(() => {
    target = getFixture();
  });
  QUnit.test("CustomWidget renders correctly", async (assert) => {
    const props = {
      record: { data: { name: "Test" } },
      name: "custom_field",
    };
    await mount(CustomWidget, target, { props });
    assert.containsOnce(target, ".o_custom_widget");
    assert.strictEqual(
      target.querySelector(".o_custom_widget h4").textContent,
      "Custom Widget"
    );
  });
});
