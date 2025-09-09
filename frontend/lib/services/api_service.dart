import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'https://chatbox-0lz7.onrender.com';

  Future<bool> signup(String username, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/signup'),
      body: jsonEncode({"username": username, "password": password}),
      headers: {'Content-Type': 'application/json'},
    );
    return res.statusCode == 201;
  }

  Future<bool> login(String username, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/login'),
      body: jsonEncode({"username": username, "password": password}),
      headers: {'Content-Type': 'application/json'},
    );
    return res.statusCode == 200;
  }

  Future<List<String>> getOnlineUsers() async {
    final res = await http.get(Uri.parse('$baseUrl/users/online'));
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return List<String>.from(data['online_users']);
    } else {
      return [];
    }
  }

  Future<List<String>> getAllUsers() async {
  final res = await http.get(Uri.parse('$baseUrl/users'));
  if (res.statusCode == 200) {
    final data = jsonDecode(res.body);
    return List<String>.from(data['users']);
  } else {
    return [];
  }
}


  Future<List<Map<String, dynamic>>> getOfflineMessages(String username) async {
    final res = await http.get(Uri.parse('$baseUrl/messages/$username'));
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return List<Map<String, dynamic>>.from(data['messages']);
    } else {
      return [];
    }
  }
}
