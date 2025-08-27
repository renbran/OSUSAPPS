/** @odoo-module **/
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

export class CustomCharField extends CharField {
  static template = "osus_enterprise_module.CustomCharField";
  setup() {
    super.setup();
    useInputField({
      getValue: () => this.props.record.data[this.props.name] || "",
      refName: "input",
      parse: (value) => this.parse(value),
    });
  }
  parse(value) {
    return value.trim().toUpperCase();
  }
  get formattedValue() {
    const value = this.props.record.data[this.props.name];
    return value ? `Custom: ${value}` : "";
  }
}
registry.category("fields").add("custom_char", CustomCharField);
