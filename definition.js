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
  // Import và khởi tạo mqtt như trước
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var server   = block.getFieldValue('SERVER');
  var username = Blockly.Python.valueToCode(block, 'USERNAME', Blockly.Python.ORDER_ATOMIC);
  var key      = Blockly.Python.valueToCode(block, 'KEY',      Blockly.Python.ORDER_ATOMIC);

  // Sinh biến TOKEN toàn cục để các block khác dùng
  Blockly.Python.definitions_['mqtt_token'] = 'TOKEN = ' + key;

  // Code connect và subscribe-down luôn trong cùng 1 chỗ (tuỳ chọn)
  var code  = `mqtt.connect_broker(server='${server}', username=${username}, password=${key})\n`;
  return code;
};


// --- definition.js ---

Blockly.Blocks['yolobit_mqtt_subscribe_and_show_pins'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("lấy cấu hình xuống và hiển thị pin");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(230);
    this.setTooltip("Subscribe eoh/chip/{TOKEN}/down rồi in Virtual pin → config_id");
    this.setHelpUrl("");
  }
};

Blockly.Python['yolobit_mqtt_subscribe_and_show_pins'] = function(block) {
  // đảm bảo import mqtt và TOKEN có sẵn
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  // định nghĩa callback in ra pin→config_id
  var funcName = Blockly.Python.provideFunction_(
    'print_virtual_pins',
    [
      'def %FUNCTION%(msg):',
      '  # payload JSON đã được lưu vào mqtt.virtual_pins',
      '  for pin, cfg in mqtt.virtual_pins.items():',
      '    print("Virtual pin V%d -> config_id %d" % (pin, cfg))'
    ].join('\n')
  );
  // subscribe đúng đường down
  var code = 'mqtt.on_receive_message(' +
             '"eoh/chip/%s/down" % TOKEN, ' +
             funcName +
             ')\n';
  return code;
};

// Gửi dữ liệu lên Virtual pin
Blockly.Blocks['yolobit_mqtt_publish_value'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck("Number")
        .appendField("gửi");
    this.appendDummyInput()
        .appendField("lên V")
        .appendField(new Blockly.FieldDropdown([
          ["V0","0"], ["V1","1"], ["V2","2"], ["V3","3"],
          ["V4","4"], ["V5","5"], ["V6","6"], ["V7","7"],
          ["V8","8"], ["V9","9"]
        ]), "PIN");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(230);
    this.setTooltip("Gửi giá trị NUMBER lên Virtual pin Vn");
    this.setHelpUrl("");
  }
};

Blockly.Python['yolobit_mqtt_publish_value'] = function(block) {
  // đảm bảo đã import mqtt
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var valueCode = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC) || '0';
  var pin = block.getFieldValue('PIN');
  // gọi method virtual_write(pin, value)
  var code = `mqtt.virtual_write(${pin}, ${valueCode})\n`;
  return code;
};
