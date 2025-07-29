import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../models/message.dart';
import '../services/websocket_service.dart';

class ChatScreen extends StatefulWidget {
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _wsService = WebSocketService();

  String? _toUser;

  @override
  void initState() {
    super.initState();
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);

    _wsService.connect(
      authProvider.user!.username,
      '<your_password>', // Add logic to pass stored password
      (Message msg) {
        chatProvider.addMessage(msg);
      },
    );
  }

  @override
  void dispose() {
    _wsService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final chatProvider = Provider.of<ChatProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('Chat (${authProvider.user?.username})'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: chatProvider.messages.length,
              itemBuilder: (_, index) {
                final msg = chatProvider.messages[index];
                return ListTile(
                  title: Text('${msg.from}: ${msg.message}'),
                );
              },
            ),
          ),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration: InputDecoration(hintText: 'Message'),
                ),
              ),
              IconButton(
                icon: Icon(Icons.send),
                onPressed: () {
                  if (_controller.text.isNotEmpty && _toUser != null) {
                    _wsService.sendMessage(_toUser!, _controller.text);
                    Provider.of<ChatProvider>(context, listen: false)
                        .addMessage(Message(
                      from: authProvider.user!.username,
                      to: _toUser!,
                      message: _controller.text,
                    ));
                    _controller.clear();
                  }
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}
