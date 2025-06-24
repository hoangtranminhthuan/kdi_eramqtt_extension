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
            ["OhStem", "mqtt.ohstem.vn"],
            ["Adafruit.IO", "io.adafruit.com"]
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

Blockly.Blocks["yolobit_mqtt_connect_custom_servers"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      nextStatement: null,
      tooltip: "Kết nối đến server MQTT được chọn",
      message0: "kết nối đến server %1 port %2 username %3 password %4 %5",
      previousStatement: null,
      args0: [
        { type: "input_value", name: "SERVER", check: "String" },
        { type: "input_value", name: "PORT", check: "Number" },
        { type: "input_value", name: "USERNAME", check: "String" },
        { type: "input_value", name: "KEY", check: "String" },
        { type: "input_dummy" },
      ],
      helpUrl: "",
    });
  },
};

Blockly.Blocks["yolobit_mqtt_publish"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      nextStatement: null,
      tooltip: "Gửi thông tin lên server",
      message0: "gửi %1 %2 đến chủ đề %3 %4",
      previousStatement: null,
      args0: [
        {
          type: "input_dummy",
        },
        {
          type: "input_value",
          name: "MESSAGE",
        },
        {
          type: "input_dummy",
        },
        {
          type: "input_value",
          name: "TOPIC",
        },
      ],
      helpUrl: "",
    });
  },
};


Blockly.Blocks["yolobit_mqtt_check_message"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      nextStatement: null,
      tooltip: "Cập nhật thông tin từ server",
      message0: "cập nhật thông tin từ server",
      previousStatement: null,
      helpUrl: "",
    });
  },
};

Blockly.Blocks["yolobit_mqtt_on_receive_message"] = {
  init: function () {
    this.jsonInit({
      colour: "#e65722",
      tooltip: "Khai báo lệnh xử lý khi có thông tin từ server gửi vào một chủ đề nào đó",
      message0: "khi nhận được %1 gửi vào chủ đề %2 %3 %4 %5",
      previousStatement: null,
      nextStatement: null,
      args0: [
        {
          variable: "thông tin",
          type: "field_variable",
          name: "message",
        },
        {
          type: "input_dummy",
        },
        {
          type: "input_value",
          name: "TOPIC",
        },
        { type: "input_dummy" },
        { type: "input_statement", name: "ACTION" },
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
  var value_server = block.getFieldValue('SERVER');
  var value_username = Blockly.Python.valueToCode(block, 'USERNAME', Blockly.Python.ORDER_ATOMIC);
  var value_key = Blockly.Python.valueToCode(block, 'KEY', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = "mqtt.connect_broker(server='" + value_server + "', port=1883, username=" + value_username + ", password=" + value_key + ")\n";
  return code;
};

Blockly.Python['yolobit_mqtt_connect_custom_servers'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var value_server = Blockly.Python.valueToCode(block, 'SERVER', Blockly.Python.ORDER_ATOMIC);
  var value_port = Blockly.Python.valueToCode(block, 'PORT', Blockly.Python.ORDER_ATOMIC);
  var value_username = Blockly.Python.valueToCode(block, 'USERNAME', Blockly.Python.ORDER_ATOMIC);
  var value_key = Blockly.Python.valueToCode(block, 'KEY', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = "mqtt.connect_broker(server=" + value_server + ", port=" + value_port + ", username=" + value_username + ", password=" + value_key + ")\n";
  return code;
};

Blockly.Python['yolobit_mqtt_is_connected'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var code = 'mqtt.is_connected()';
  return [code, Blockly.Python.ORDER_MEMBER];
};
Blockly.Python['yolobit_mqtt_publish'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var value_message = Blockly.Python.valueToCode(block, 'MESSAGE', Blockly.Python.ORDER_ATOMIC);
  var value_topic = Blockly.Python.valueToCode(block, 'TOPIC', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = 'mqtt.publish(' + value_topic + ', ' + value_message + ')\n';
  return code;
};

Blockly.Python['yolobit_mqtt_check_message'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  // TODO: Assemble Python into code variable.
  var code = 'mqtt.check_message()\n';
  return code;
};

Blockly.Python['yolobit_mqtt_on_receive_message'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  var variable_message = Blockly.Python.variableDB_.getName(block.getFieldValue('message'), Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE);
  var value_topic = Blockly.Python.valueToCode(block, 'TOPIC', Blockly.Python.ORDER_ATOMIC);
  var statements_action = Blockly.Python.statementToCode(block, 'ACTION');
  // TODO: Assemble Python into code variable.
  var globals = [];
  var varName;
  var workspace = block.workspace;
  var variables = workspace.getAllVariables() || [];
  for (var i = 0, variable; variable = variables[i]; i++) {
    varName = variable.name;
    if (Blockly.Python.variableDB_.getName(varName, Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE) != variable_message) {
      globals.push(Blockly.Python.variableDB_.getName(varName,
        Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE));
    }
  }
  globals = globals.length ? Blockly.Python.INDENT + 'global ' + globals.join(', ') : '';

  var cbFunctionName = Blockly.Python.provideFunction_(
    'on_mqtt_message_receive_callback_' + value_topic,
    ['def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(' + variable_message + '):',
      globals,
      statements_action || Blockly.Python.PASS
    ]);
  
  var code = 'mqtt.on_receive_message(' + value_topic + ', ' + cbFunctionName + ')\n';
  return code;
};

Blockly.Python['yolobit_wifi_on_receive_message_from_dashboard'] = function(block) {
  Blockly.Python.definitions_['import_wifi'] = 'from wifi import *';
  var variable_message = Blockly.Python.variableDB_.getName(block.getFieldValue('message'), Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE);
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var statements_action = Blockly.Python.statementToCode(block, 'ACTION');
  // TODO: Assemble Python into code variable.
  var globals = [];
  var varName;
  var workspace = block.workspace;
  var variables = workspace.getAllVariables() || [];
  for (var i = 0, variable; variable = variables[i]; i++) {
    varName = variable.name;
    if (Blockly.Python.variableDB_.getName(varName, Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE) != variable_message) {
      globals.push(Blockly.Python.variableDB_.getName(varName,
        Blockly.Names.NameType?Blockly.Names.NameType.VARIABLE:Blockly.Variables.NAME_TYPE));
    }
  }
  globals = globals.length ? Blockly.Python.INDENT + 'global ' + globals.join(', ') : '';

  var cbFunctionName = Blockly.Python.provideFunction_(
    'on_wifi_message_receive_callback_' + block.id,
    ['def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(' + variable_message + '):',
      globals,
      statements_action || Blockly.Python.PASS
    ]);

  var code = 'on_receive_message("' + dropdown_channel + '", ' + cbFunctionName + ')\n';
  Blockly.Python.definitions_['on_wifi_message_receive_callback_' + block.id + '_statement'] = code;
  return '';
};
Blockly.Blocks["yolobit_mqtt_check_connection"] = {
  init: function () {
    this.jsonInit(
      {
      "type": "yolobit_mqtt_check_connection",
      "message0": "đang kết nối wifi",
      "output": "Boolean",
      "colour": "#e65722",
      "tooltip": "",
      "helpUrl": ""
      }
    );
}
};

Blockly.Python['yolobit_mqtt_check_connection'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import *';
  // TODO: Assemble Python into code variable.
  var code = 'mqtt.wifi_connected()';
  return [code, Blockly.Python.ORDER_NONE];
};
