import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatelessWidget {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final ApiService _apiService = ApiService();

  LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _usernameController,
              decoration: InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            ElevatedButton(
              child: Text('Login'),
              onPressed: () async {
                bool success = await _apiService.login(
                  _usernameController.text,
                  _passwordController.text,
                );
                if (success) {
                  authProvider.login(_usernameController.text, _passwordController.text);
                  Navigator.pushReplacementNamed(context, '/chat');
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Invalid credentials')),
                  );
                }
              },
            ),
            TextButton(
              child: Text('Don\'t have an account? Sign up'),
              onPressed: () {
                Navigator.pushNamed(context, '/signup');
              },
            ),
          ],
        ),
      ),
    );
  }
}
