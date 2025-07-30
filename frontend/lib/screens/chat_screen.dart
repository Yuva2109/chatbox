import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../models/message.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _wsService = WebSocketService();
  final _apiService = ApiService();

  String? _toUser;
  List<String> _onlineUsers = [];

  @override
  void initState() {
    super.initState();

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);

    final password = authProvider.user!.password ; 
    _wsService.connect(authProvider.user!.username, password, (Message msg) {
      chatProvider.addMessage(msg);
    });

    _loadOnlineUsers();
  }

  void _loadOnlineUsers() async {
    final users = await _apiService.getOnlineUsers();
    setState(() {
      _onlineUsers = users;
    });
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
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadOnlineUsers,
            tooltip: 'Refresh Users',
          ),
        ],
      ),
      body: Row(
        children: [
          // Online users panel (like WhatsApp)
          Container(
            width: 200,
            color: Colors.grey[200],
            child: ListView.builder(
              itemCount: _onlineUsers.length,
              itemBuilder: (_, index) {
                final user = _onlineUsers[index];
                if (user == authProvider.user!.username) return SizedBox.shrink(); // skip self
                return ListTile(
                  title: Text(user),
                  selected: user == _toUser,
                  onTap: () {
                    setState(() {
                      _toUser = user;
                    });
                  },
                );
              },
            ),
          ),

          // Chat window
          Expanded(
            child: Column(
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
                        decoration: InputDecoration(
                          hintText: _toUser == null
                              ? 'Select user to chat'
                              : 'Message to $_toUser',
                        ),
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.send),
                      onPressed: () {
                        if (_controller.text.isNotEmpty && _toUser != null) {
                          _wsService.sendMessage(_toUser!, _controller.text);
                          chatProvider.addMessage(Message(
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
          ),
        ],
      ),
    );
  }
}
