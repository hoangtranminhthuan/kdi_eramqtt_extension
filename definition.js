Blockly.Blocks["yolobit_mqtt_connect_wifi"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      nextStatement: null,
      tooltip: "Kết nối vào mạng WiFi",
      message0: "kết nối WiFi %1 %2 mật khẩu %3 %4",
      previousStatement: null,
      args0: [
        { type: "input_dummy" },
        { type: "input_value", name: "WIFI", check: "String" },
        { type: "input_dummy" },
        { type: "input_value", name: "PASSWORD", check: "String" },
      ],
      helpUrl: "",
    });
  },
};

Blockly.Blocks["yolobit_mqtt_connect_default_servers"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      nextStatement: null,
      tooltip: "Kết nối đến server MQTT được chọn",
      message0: "kết nối đến server %1 với username %2 key %3 %4",
      previousStatement: null,
      args0: [
        {
          type: "field_dropdown",
          name: "SERVER",
          options: [
            ["EOH", "mqtt1.eoh.io"]
          ],
        },
        { type: "input_value", name: "USERNAME", check: "String" },
        { type: "input_value", name: "KEY", check: "String" },
        { type: "input_dummy" },
      ],
      helpUrl: "",
    });
  },
};

'use strict';

// Any imports need to be reserved words
Blockly.Python.addReservedWords('wifi');

Blockly.Python['yolobit_mqtt_connect_wifi'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var value_wifi = Blockly.Python.valueToCode(block, 'WIFI', Blockly.Python.ORDER_ATOMIC);
  var value_password = Blockly.Python.valueToCode(block, 'PASSWORD', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = 'mqtt.connect_wifi(' + value_wifi + ', ' + value_password + ')\n';
  return code;
};

Blockly.Python['yolobit_mqtt_connect_default_servers'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var server   = block.getFieldValue('SERVER');
  var username = Blockly.Python.valueToCode(block, 'USERNAME', Blockly.Python.ORDER_ATOMIC);
  var key      = Blockly.Python.valueToCode(block, 'KEY',      Blockly.Python.ORDER_ATOMIC);
  var code = `mqtt.connect_broker(server='${server}', username=${username}, password=${key})\n`;
  return code;
};

Blockly.Blocks['yolobit_mqtt_virtual_pin_map'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("bản đồ Virtual pin → config_id");
    this.setOutput(true, null);
    this.setColour(230);
    this.setTooltip("Trả về dict { 'V1':12345, 'V3':67890, … }");
    this.setHelpUrl("");
  }
};

Blockly.Python['yolobit_mqtt_virtual_pin_map'] = function(block) {
  // Sinh dict comprehension: key 'V<pin>' → value config_id
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var code = "{'V%d' % pin: mqtt.virtual_pins[pin] for pin in mqtt.virtual_pins}";
  return [code, Blockly.Python.ORDER_ATOMIC];
};
