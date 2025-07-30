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
  List<Map<String, dynamic>> _combinedUsers = [];

  @override
  void initState() {
    super.initState();

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    final password = authProvider.user!.password;

    _wsService.onOnlineUsersUpdated = (onlineUsers) {
      _combineUsers(onlineUsers);
    };

    _wsService.connect(authProvider.user!.username, password, (Message msg) {
      chatProvider.addMessage(msg);
    });

    _loadUsers();
  }

  void _loadUsers() async {
    final allUsers = await _apiService.getAllUsers();
    final onlineUsers = await _apiService.getOnlineUsers();
    _combineUsers(onlineUsers, allUsers: allUsers);
  }

  void _combineUsers(List<String> online, {List<String>? allUsers}) async {
    if (allUsers == null) {
      allUsers = await _apiService.getAllUsers();
    }

    final combined = allUsers.map((u) {
      return {
        'username': u,
        'online': online.contains(u),
      };
    }).toList();

    setState(() {
      _combinedUsers = combined;
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
            onPressed: _loadUsers,
            tooltip: 'Refresh Users',
          ),
        ],
      ),
      body: Row(
        children: [
          // LEFT SIDEBAR — all users with online/offline dot
          Container(
            width: 200,
            color: Colors.grey[200],
            child: ListView.builder(
              itemCount: _combinedUsers.length,
              itemBuilder: (_, index) {
                final user = _combinedUsers[index];
                final username = user['username'];
                final isOnline = user['online'];

                if (username == authProvider.user!.username) {
                  return SizedBox.shrink(); // skip self
                }

                return ListTile(
                  leading: Icon(
                    Icons.circle,
                    size: 12,
                    color: isOnline ? Colors.green : Colors.red,
                  ),
                  title: Text(username),
                  selected: username == _toUser,
                  onTap: () {
                    setState(() {
                      _toUser = username;
                    });
                  },
                );
              },
            ),
          ),

          // RIGHT CHAT PANEL
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
