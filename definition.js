var virtualPins = [
  ["V0", "0"],
  ["V1", "1"],
  ["V2", "2"],
  ["V3", "3"],
  ["V4", "4"],
  ["V5", "5"],
  ["V6", "6"],
  ["V7", "7"],
  ["V8", "8"],
  ["V9", "9"],
  ["V10", "10"],
  ["V11", "11"],
  ["V12", "12"],
  ["V13", "13"],
  ["V14", "14"],
  ["V15", "15"],
  ["V16", "16"],
  ["V17", "17"],
  ["V18", "18"],
  ["V19", "19"],
  ["V20", "20"]
];

Blockly.Blocks['era_mqtt_connect'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'kết nối Era với WiFi %1 password %2 %3 token %4',
      args0: [
        { type: 'field_input', name: 'WIFI', text: 'ssid' },
        { type: 'field_input', name: 'PASSWORD', text: 'password' },
        { type: 'input_dummy' },
        { type: 'field_input', name: 'TOKEN', text: 'chip01' }
      ],
      previousStatement: null,
      nextStatement: null,
      tooltip: 'Kết nối WiFi và MQTT đến ERA broker',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_connect'] = function(block) {
  var wifi = block.getFieldValue('WIFI');
  var password = block.getFieldValue('PASSWORD');
  var chip = block.getFieldValue('TOKEN');
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import MQTT';
  var code = "mqtt = MQTT('" + wifi + "', '" + password + "', '" + chip + "')\n";
  code += 'mqtt.connect_wifi()\n';
  code += 'mqtt.connect_broker()\n';
  return code;
};

Blockly.Blocks['era_mqtt_publish'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'gửi %1 %2 lên %3 %4',
      args0: [
        { type: 'input_dummy' },
        { type: 'input_value', name: 'MESSAGE' },
        { type: 'field_dropdown', name: 'TOPIC', options: virtualPins },
        { type: 'input_dummy' }
      ],
      previousStatement: null,
      nextStatement: null,
      tooltip: 'Publish giá trị đến topic /info',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_publish'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import MQTT';
  var value = Blockly.Python.valueToCode(block, 'MESSAGE', Blockly.Python.ORDER_ATOMIC) || '0';
  var code = 'mqtt.publish(' + value + ')\n';
  return code;
};

Blockly.Blocks['era_mqtt_on_receive_message'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'khi %1 nhận thông tin %2 %3',
      args0: [
        { type: 'field_dropdown', name: 'TOPIC', options: virtualPins },
        { type: 'input_dummy' },
        { type: 'input_statement', name: 'ACTION' }
      ],
      previousStatement: null,
      nextStatement: null,
      tooltip: 'Đăng ký callback khi nhận tin từ broker',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_on_receive_message'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import MQTT';
  var pin = block.getFieldValue('TOPIC');
  var statements = Blockly.Python.statementToCode(block, 'ACTION');
  var funcName = Blockly.Python.provideFunction_(
    'on_receive_virtual_' + pin,
    ['def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(msg):',
     statements || Blockly.Python.PASS
    ]
  );
  var code = "mqtt.on_receive_message('/virtual_pin/" + pin + "', " + funcName + ")\n";
  return code;
};

Blockly.Blocks['era_mqtt_compare_value'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      output: 'Boolean',
      message0: 'giá trị nhận được là %1 %2',
      args0: [
        { type: 'input_value', name: 'VALUE' },
        { type: 'input_dummy' }
      ],
      tooltip: '',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_compare_value'] = function(block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC);
  var code = 'msg == ' + value;
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['era_mqtt_get_value'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      output: null,
      message0: 'giá trị nhận được',
      args0: [],
      tooltip: 'Đọc payload message',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_get_value'] = function(block) {
  var code = 'msg';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['era_mqtt_get_topic'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      output: null,
      message0: 'topic nhận được',
      args0: [],
      tooltip: 'Đọc topic nhận được',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_get_topic'] = function(block) {
  var code = 'topic';
  return [code, Blockly.Python.ORDER_NONE];
};
