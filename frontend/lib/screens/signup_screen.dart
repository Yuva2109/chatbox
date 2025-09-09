import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SignupScreen extends StatelessWidget {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final ApiService _apiService = ApiService();

  SignupScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Sign Up')),
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
              child: Text('Sign Up'),
              onPressed: () async {
                bool success = await _apiService.signup(
                  _usernameController.text,
                  _passwordController.text,
                );
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Sign up successful! Please login.')),
                  );
                  Navigator.pop(context);
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Username already exists.')),
                  );
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
