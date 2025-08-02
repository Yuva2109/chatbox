import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/message.dart';

typedef OnMessageReceived = void Function(Message);

class WebSocketService {
  WebSocketChannel? _channel;

  Function(List<String>)? onOnlineUsersUpdated;

  Function(List<String>, List<String>)? onPresenceUpdate; // ✅

  void connect(String username, String password, OnMessageReceived onMessage) {
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://172.22.155.137:12345'),
    );

    _channel!.stream.listen((message) {
      final data = jsonDecode(message);

      if (data['type'] == 'message') {
        onMessage(Message(
          from: data['from'],
          to: username,
          message: data['message'],
        ));
      } else if (data['type'] == 'presence_update') {
        if (onPresenceUpdate != null) {
          final online = List<String>.from(data['online_users']);
          final all = List<String>.from(data['all_users']);
          onPresenceUpdate!(online, all);
        }
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
