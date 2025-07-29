import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/message.dart';

typedef OnMessageReceived = void Function(Message);

class WebSocketService {
  WebSocketChannel? _channel;

  void connect(String username, String password, OnMessageReceived onMessage) {
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://10.137.245.137:12345'),
    );

    _channel!.stream.listen((message) {
      final data = jsonDecode(message);
      if (data['type'] == 'message') {
        onMessage(Message(
          from: data['from'],
          to: username,
          message: data['message'],
        ));
      }
    });

    _send({
      "type": "login",
      "username": username,
      "password": password,
    });
  }

  void sendMessage(String to, String message) {
    _send({
      "type": "message",
      "to": to,
      "message": message,
    });
  }

  void _send(Map<String, dynamic> data) {
    _channel?.sink.add(jsonEncode(data));
  }

  void disconnect() {
    _channel?.sink.close();
  }
}
