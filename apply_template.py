#!/usr/bin/env python3

import os
import sys
import subprocess
import re
import shutil
from pathlib import Path

class FlutterTemplateSetup:
    def __init__(self, app_name=None):
        self.app_name = app_name
        self.parent_dir = os.path.dirname(os.path.dirname(os.getcwd()))

    def get_app_name(self):
        if self.app_name:
            return self.app_name

        print("📝 App Name Setup")
        print("====================")
        print("Please enter your app name.")
        print("Requirements:")
        print("- Lowercase letters only")
        print("- Can include numbers and underscores")
        print("- Must start with a letter")
        print("====================")

        while True:
            app_name = input("\n> Enter app name: ").strip()
            if re.match(r'^[a-z][a-z0-9_]*$', app_name):
                self.app_name = app_name
                return app_name
            else:
                print(f"❌ Invalid app name: '{app_name}'")
                print("App name must be lowercase, start with a letter, and contain only letters, numbers, and underscores.")

    def create_flutter_project(self):
        print("🚀 Creating new Flutter project...")
        
        # Create new directory and change into it
        project_dir = os.path.join(self.parent_dir, self.app_name)
        os.makedirs(project_dir, exist_ok=True)
        os.chdir(project_dir)
        
        # Create the project
        print(f"Creating project {self.app_name}...")
        subprocess.run([
            "flutter", "create",
            "--org", "com.app.template",
            "--project-name", self.app_name,
            "--platforms", "ios,android,web,macos",
            "."
        ], check=True)
        
        # Enable web and macOS support
        subprocess.run(["flutter", "config", "--enable-web"], check=True)
        subprocess.run(["flutter", "config", "--enable-macos-desktop"], check=True)
        
        # Set initial version to 0.0.1
        print("Setting initial version to 0.0.1...")
        with open("pubspec.yaml", "r") as f:
            content = f.read()
        content = content.replace("version: 1.0.0+1", "version: 0.0.1+1")
        with open("pubspec.yaml", "w") as f:
            f.write(content)
        
        print("Project created successfully!")

    def update_pubspec(self):
        print("📦 Updating pubspec.yaml with additional dependencies...")
        
        # Additional dependencies to add
        additional_deps = """
  # State management and dependency injection
  flutter_riverpod: ^2.4.9
  path_provider: ^2.1.1  # Essential for file operations
  go_router: ^13.2.0  # Navigation
"""
        
        # Read the pubspec.yaml file
        with open("pubspec.yaml", "r") as f:
            lines = f.readlines()
        
        # Find the line before dev_dependencies
        deps_end = None
        for i, line in enumerate(lines):
            if line.strip() == "dev_dependencies:":
                deps_end = i
                break
        
        if deps_end is None:
            raise Exception("Could not find dev_dependencies section in pubspec.yaml")
        
        # Insert additional dependencies
        lines.insert(deps_end, additional_deps)
        
        # Ensure flutter.uses-material-design is true
        if not any("uses-material-design: true" in line for line in lines):
            lines.append("\n  # The following section is specific to Flutter packages.\nflutter:\n  uses-material-design: true\n")
        
        # Write the updated content back
        with open("pubspec.yaml", "w") as f:
            f.writelines(lines)

    def create_provider_structure(self):
        print("🔄 Creating core provider structure...")
        
        # Create provider directories
        os.makedirs("lib/core/providers", exist_ok=True)
        os.makedirs("lib/core/states", exist_ok=True)
        
        # Create app providers file
        with open("lib/core/providers/app_providers.dart", "w") as f:
            f.write(f"""import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{self.app_name}/core/providers/theme_provider.dart';

// App-wide providers
final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {{
  return ThemeNotifier();
}});
""")
        
        # Create theme provider file
        with open("lib/core/providers/theme_provider.dart", "w") as f:
            f.write("""import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ThemeNotifier extends StateNotifier<ThemeMode> {
  ThemeNotifier() : super(ThemeMode.dark);

  void toggleTheme() {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
  }
}
""")
        
        # Create auth provider file
        with open("lib/core/providers/auth_provider.dart", "w") as f:
            f.write("""import 'package:flutter_riverpod/flutter_riverpod.dart';

class AuthState {
  final bool isAuthenticated;
  final String? userId;

  AuthState({this.isAuthenticated = false, this.userId});

  AuthState copyWith({bool? isAuthenticated, String? userId}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      userId: userId ?? this.userId,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  void login(String userId) {
    state = state.copyWith(isAuthenticated: true, userId: userId);
  }

  void logout() {
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
""")

    def create_router_config(self):
        print("🛣️ Creating router configuration...")
        
        # Create router directory
        os.makedirs("lib/router", exist_ok=True)
        
        # Create router configuration file
        with open("lib/router/router.dart", "w") as f:
            f.write(f"""import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{self.app_name}/core/providers/app_providers.dart';

/// A provider that exposes the GoRouter instance
/// This allows the router to be accessed from anywhere in the app
/// and makes it easy to test and mock
final routerProvider = Provider<GoRouter>((ref) {{
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: '/second',
        builder: (context, state) => const SecondPage(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Error: \${{state.error}}'),
      ),
    ),
  );
}});

class HomePage extends ConsumerWidget {{
  const HomePage({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    final themeMode = ref.watch(themeProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('{self.app_name}'),
        actions: [
          IconButton(
            icon: Icon(
              themeMode == ThemeMode.dark ? Icons.light_mode : Icons.dark_mode,
            ),
            onPressed: () => ref.read(themeProvider.notifier).toggleTheme(),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Welcome to {self.app_name}',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            Text(
              'This is your home page',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/second'),
              child: const Text('Go to Second Page'),
            ),
          ],
        ),
      ),
    );
  }}
}}

class SecondPage extends ConsumerWidget {{
  const SecondPage({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    final themeMode = ref.watch(themeProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('{self.app_name} - Second Page'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
        actions: [
          IconButton(
            icon: Icon(
              themeMode == ThemeMode.dark ? Icons.light_mode : Icons.dark_mode,
            ),
            onPressed: () => ref.read(themeProvider.notifier).toggleTheme(),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Second Page',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            Text(
              'You can navigate back to the home page',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/'),
              child: const Text('Go Back Home'),
            ),
          ],
        ),
      ),
    );
  }}
}}
""")

    def add_backend_dependencies(self):
        print("📦 Adding backend dependencies...")
        
        # Additional dependencies to add
        additional_deps = """
  # Backend communication
  dio: ^5.3.3
"""
        
        # Read the pubspec.yaml file
        with open("pubspec.yaml", "r") as f:
            lines = f.readlines()
        
        # Find the line before dev_dependencies
        deps_end = None
        for i, line in enumerate(lines):
            if line.strip() == "dev_dependencies:":
                deps_end = i
                break
        
        if deps_end is None:
            raise Exception("Could not find dev_dependencies section in pubspec.yaml")
        
        # Insert additional dependencies
        lines.insert(deps_end, additional_deps)
        
        # Write the updated content back
        with open("pubspec.yaml", "w") as f:
            f.writelines(lines)

    def create_backend_structure(self):
        print("🔄 Creating backend structure...")
        
        # Create backend directory
        os.makedirs("lib/core/backend", exist_ok=True)
        
        # Create API client
        with open("lib/core/backend/api_client.dart", "w") as f:
            f.write("""import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// A simple HTTP client for making API requests
class ApiClient {
  final Dio _dio;
  final String baseUrl;

  ApiClient({required this.baseUrl}) : _dio = Dio() {
    _dio.options.baseUrl = baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 5);
    _dio.options.receiveTimeout = const Duration(seconds: 3);
  }

  /// Makes a GET request to the specified path
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Makes a POST request to the specified path
  Future<Response> post(String path, {dynamic data}) async {
    try {
      return await _dio.post(path, data: data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return Exception('Request timed out');
      case DioExceptionType.badResponse:
        return Exception('Server error: \${error.response?.statusCode}');
      default:
        return Exception('Network error: \${error.message}');
    }
  }
}

/// Provider for the API client
final apiClientProvider = Provider<ApiClient>((ref) {
  // In a real app, this would come from environment configuration
  return ApiClient(baseUrl: 'https://api.example.com');
});
""")

    def create_theme_system(self):
        print("🎨 Implementing theme system...")
        
        # Create theme directory
        os.makedirs("lib/theme", exist_ok=True)
        
        # Create app_theme.dart
        with open("lib/theme/app_theme.dart", "w") as f:
            f.write("""import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.light,
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: Colors.grey[900],
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.grey[850],
        foregroundColor: Colors.white,
      ),
    );
  }
}
""")

    def update_main_dart(self):
        print("📝 Updating main.dart with theme support...")
        with open("lib/main.dart", "w") as f:
            f.write(f"""import 'package:{self.app_name}/theme/app_theme.dart';
import 'package:{self.app_name}/core/providers/app_providers.dart';
import 'package:{self.app_name}/router/router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {{
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}}

class MyApp extends ConsumerWidget {{
  const MyApp({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    final themeMode = ref.watch(themeProvider);
    final router = ref.watch(routerProvider);
    
    return MaterialApp.router(
      title: '{self.app_name}',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }}
}}
""")

    def update_widget_test(self):
        print("🧪 Updating widget test...")
        with open("test/widget_test.dart", "w") as f:
            f.write(f"""import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{self.app_name}/main.dart';

void main() {{
  group('App', () {{
    testWidgets('displays correct app name in AppBar', (WidgetTester tester) async {{
      await tester.pumpWidget(
        const ProviderScope(
          child: MyApp(),
        ),
      );

      expect(find.text('{self.app_name}'), findsOneWidget);
      
      final appBarFinder = find.byType(AppBar);
      expect(appBarFinder, findsOneWidget);
      
      expect(
        find.descendant(
          of: appBarFinder,
          matching: find.text('{self.app_name}'),
        ),
        findsOneWidget,
      );
    }});
  }});
}}
""")

    def run(self):
        print("🎯 Flutter Template Setup")

        # Get app name
        self.get_app_name()
        print(f"📝 Using app name: {self.app_name}")

        # Step 1: Create new Flutter project
        self.create_flutter_project()

        # Step 2: Verify Flutter project
        print("🔍 Step 2: Verifying Flutter project...")
        subprocess.run(["flutter", "doctor"], check=True)
        subprocess.run(["flutter", "pub", "get"], check=True)

        # Step 3: Update pubspec.yaml with additional dependencies
        print("📦 Step 3: Updating dependencies in pubspec.yaml...")
        self.update_pubspec()

        # Step 4: Install dependencies
        print("📥 Step 4: Installing dependencies...")
        subprocess.run(["flutter", "pub", "get"], check=True)

        # Step 5: Create core provider structure
        print("🔄 Step 5: Creating core provider structure...")
        self.create_provider_structure()

        # Step 6: Implement theme system
        print("🎨 Step 6: Implementing theme system...")
        self.create_theme_system()

        # Step 7: Create router configuration
        print("🛣️ Step 7: Creating router configuration...")
        self.create_router_config()

        # Step 8: Update main.dart with proper theme implementation
        print("📝 Step 8: Updating main.dart with theme support...")
        self.update_main_dart()

        # Step 9: Update widget test
        print("🧪 Step 9: Updating widget test...")
        self.update_widget_test()

        # Step 10: Run initial test
        print("✅ Running initial test...")
        subprocess.run(["flutter", "test"], check=True)

        # Step 11: Launch the app in Chrome
        print("🚀 Launching app in Chrome...")
        subprocess.run(["flutter", "run", "-d", "chrome"], check=True)

        # Step 12: Add backend functionality
        print("🔌 Step 12: Adding backend functionality...")
        self.add_backend_dependencies()
        subprocess.run(["flutter", "pub", "get"], check=True)
        self.create_backend_structure()

        print("✅ Template setup complete!")
        print("The app is now running in Chrome. You can:")
        print("1. Press 'r' to hot reload")
        print("2. Press 'R' to hot restart")
        print("3. Press 'q' to quit")

def main():
    app_name = sys.argv[1] if len(sys.argv) > 1 else None
    setup = FlutterTemplateSetup(app_name)
    setup.run()

if __name__ == "__main__":
    main() 