import 'package:flutter/material.dart';
import '../models/user.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;

  User? get user => _user;

  void login(String username) {
    _user = User(username: username);
    notifyListeners();
  }

  void logout() {
    _user = null;
    notifyListeners();
  }
}
