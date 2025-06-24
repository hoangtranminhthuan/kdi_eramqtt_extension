var mqtt;

Blockly.Blocks['era_mqtt_connect'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'kết nối ERA WiFi %1 mật khẩu %2 chip id %3',
      args0: [
        { type: 'field_input', name: 'WIFI', text: 'ssid' },
        { type: 'field_input', name: 'PASSWORD', text: 'password' },
        { type: 'field_input', name: 'CHIP', text: 'chip01' }
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
  var chip = block.getFieldValue('CHIP');
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
      message0: 'gửi giá trị %1',
      args0: [
        { type: 'input_value', name: 'VALUE' }
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
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC) || '0';
  var code = 'mqtt.publish(' + value + ')\n';
  return code;
};

Blockly.Blocks['era_mqtt_on_receive'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'khi nhận %1 thực thi',
      args0: [
        { type: 'field_dropdown', name: 'SUFFIX', options: [
            ['/down', '/down'],
            ['virtual pin', '/virtual_pin/+']
        ] },
        { type: 'input_statement', name: 'ACTION' }
      ],
      previousStatement: null,
      nextStatement: null,
      tooltip: 'Đăng ký callback khi nhận tin từ broker',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_on_receive'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import MQTT';
  var suffix = block.getFieldValue('SUFFIX');
  var statements = Blockly.Python.statementToCode(block, 'ACTION');
  var funcName = Blockly.Python.provideFunction_(
    'on_receive_' + suffix.replace(/[^a-zA-Z0-9]/g, '_'),
    ['def ' + Blockly.Python.FUNCTION_NAME_PLACEHOLDER_ + '(msg):',
     statements || Blockly.Python.PASS
    ]
  );
  var code = "mqtt.on_receive_message('" + suffix + "', " + funcName + ")\n";
  return code;
};

Blockly.Blocks['era_mqtt_check'] = {
  init: function() {
    this.jsonInit({
      colour: '#ff8d12',
      message0: 'kiểm tra tin nhắn',
      previousStatement: null,
      nextStatement: null,
      tooltip: 'Gọi mqtt.check_message() để nhận tin mới',
      helpUrl: ''
    });
  }
};

Blockly.Python['era_mqtt_check'] = function(block) {
  Blockly.Python.definitions_['import_mqtt'] = 'from mqtt import MQTT';
  var code = 'mqtt.check_message()\n';
  return code;
};
