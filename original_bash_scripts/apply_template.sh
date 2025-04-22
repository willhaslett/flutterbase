#!/bin/bash

# Flutter Template Setup Script
# This script implements the template specification up to step 7
# It creates a new Flutter app with theme support and initial testing

# Ensure proper terminal handling
exec < /dev/tty
exec > /dev/tty
stty sane

set -e  # Exit on error

# Function to get and validate app name
get_app_name() {
    echo "📝 App Name Setup"
    echo "===================="
    echo "Please enter your app name."
    echo "Requirements:"
    echo "- Lowercase letters only"
    echo "- Can include numbers and underscores"
    echo "- Must start with a letter"
    echo "===================="
    while true; do
        printf "\n> Enter app name: "
        read app_name
        if [[ "$app_name" =~ ^[a-z][a-z0-9_]*$ ]]; then
            break
        else
            echo "❌ Invalid app name: '$app_name'"
            echo "App name must be lowercase, start with a letter, and contain only letters, numbers, and underscores."
        fi
    done
}

# Function to create Flutter project
create_flutter_project() {
    echo "🚀 Creating new Flutter project..."
    
    # Get the parent directory path
    PARENT_DIR="$(dirname "$(pwd)")"
    
    # Create new directory and change into it
    mkdir -p "$PARENT_DIR/$app_name"
    cd "$PARENT_DIR/$app_name"
    
    # Create the project
    echo "Creating project $app_name..."
    flutter create --org com.app.template --project-name $app_name --platforms ios,android,web,macos .
    
    # Enable web and macOS support
    flutter config --enable-web
    flutter config --enable-macos-desktop
    
    # Set initial version to 0.0.1 (following semantic versioning for initial development)
    echo "Setting initial version to 0.0.1..."
    sed -i '' 's/version: 1.0.0+1/version: 0.0.1+1/' pubspec.yaml
    
    echo "Project created successfully!"
}

# Function to update pubspec.yaml with additional dependencies
update_pubspec() {
    echo "📦 Updating pubspec.yaml with additional dependencies..."
    
    # Create a temporary file for the new dependencies
    cat > temp_deps.yaml << EOL
  # State management and dependency injection
  flutter_riverpod: ^2.4.9
  path_provider: ^2.1.1  # Essential for file operations
  go_router: ^13.2.0  # Navigation
EOL

    # Find the line number where dependencies section ends
    deps_end=$(awk '/^dev_dependencies:/{ print NR-1; exit }' pubspec.yaml)
    
    # Insert our additional dependencies before dev_dependencies
    sed -i '' "${deps_end}r temp_deps.yaml" pubspec.yaml
    rm temp_deps.yaml
    
    # Ensure flutter.uses-material-design is true
    if ! grep -q "uses-material-design: true" pubspec.yaml; then
        echo "
  # The following section is specific to Flutter packages.
flutter:
  uses-material-design: true" >> pubspec.yaml
    fi
}

# Function to create core provider structure
create_provider_structure() {
    echo "🔄 Creating core provider structure..."
    
    # Create provider directories
    mkdir -p lib/core/providers
    mkdir -p lib/core/states
    
    # Create app providers file
    cat > lib/core/providers/app_providers.dart << EOL
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:$app_name/core/providers/theme_provider.dart';

// App-wide providers
final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {
  return ThemeNotifier();
});
EOL

    # Create theme provider file
    cat > lib/core/providers/theme_provider.dart << EOL
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ThemeNotifier extends StateNotifier<ThemeMode> {
  ThemeNotifier() : super(ThemeMode.dark);

  void toggleTheme() {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
  }
}
EOL

    # Create auth provider file
    cat > lib/core/providers/auth_provider.dart << EOL
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
EOL
}

# Function to create router configuration
create_router_config() {
    echo "🛣️ Creating router configuration..."
    
    # Create router directory
    mkdir -p lib/router
    
    # Create router configuration file
    cat > lib/router/router.dart << EOL
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:$app_name/core/providers/app_providers.dart';

/// A provider that exposes the GoRouter instance
/// This allows the router to be accessed from anywhere in the app
/// and makes it easy to test and mock
final routerProvider = Provider<GoRouter>((ref) {
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
        child: Text('Error: \${state.error}'),
      ),
    ),
  );
});

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('$app_name'),
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
              'Welcome to $app_name',
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
  }
}

class SecondPage extends ConsumerWidget {
  const SecondPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('$app_name - Second Page'),
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
  }
}
EOL
}

# Function to add backend dependencies
add_backend_dependencies() {
    echo "📦 Adding backend dependencies..."
    
    # Create a temporary file for the new dependencies
    cat > temp_deps.yaml << EOL
  # Backend communication
  dio: ^5.3.3
EOL

    # Find the line number where dependencies section ends
    deps_end=$(awk '/^dev_dependencies:/{ print NR-1; exit }' pubspec.yaml)
    
    # Insert our additional dependencies before dev_dependencies
    sed -i '' "${deps_end}r temp_deps.yaml" pubspec.yaml
    rm temp_deps.yaml
}

# Function to create backend structure
create_backend_structure() {
    echo "🔄 Creating backend structure..."
    
    # Create backend directory
    mkdir -p lib/core/backend
    
    # Create API client
    cat > lib/core/backend/api_client.dart << EOL
import 'package:dio/dio.dart';
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
EOL
}

# Main script execution
echo "🎯 Flutter Template Setup"

# Get app name
get_app_name
echo "📝 Using app name: $app_name"

# Step 1: Create new Flutter project
create_flutter_project

# Step 2: Verify Flutter project
echo "🔍 Step 2: Verifying Flutter project..."
flutter doctor
flutter pub get

# Step 3: Update pubspec.yaml with additional dependencies
echo "📦 Step 3: Updating dependencies in pubspec.yaml..."
update_pubspec

# Step 4: Install dependencies
echo "📥 Step 4: Installing dependencies..."
flutter pub get

# Step 5: Create core provider structure
echo "🔄 Step 5: Creating core provider structure..."
create_provider_structure

# Step 6: Implement theme system
echo "🎨 Step 6: Implementing theme system..."

# Create theme directory
mkdir -p lib/theme

# Create app_theme.dart
cat > lib/theme/app_theme.dart << 'EOL'
import 'package:flutter/material.dart';

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
EOL

# Step 7: Create router configuration
echo "🛣️ Step 7: Creating router configuration..."
create_router_config

# Step 8: Update main.dart with proper theme implementation
echo "📝 Step 8: Updating main.dart with theme support..."
cat > lib/main.dart << EOL
import 'package:$app_name/theme/app_theme.dart';
import 'package:$app_name/core/providers/app_providers.dart';
import 'package:$app_name/router/router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    final router = ref.watch(routerProvider);
    
    return MaterialApp.router(
      title: '$app_name',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}
EOL

# Step 9: Update widget test
echo "🧪 Step 9: Updating widget test..."
cat > test/widget_test.dart << EOL
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:$app_name/main.dart';

void main() {
  group('App', () {
    testWidgets('displays correct app name in AppBar', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MyApp(),
        ),
      );

      expect(find.text('$app_name'), findsOneWidget);
      
      final appBarFinder = find.byType(AppBar);
      expect(appBarFinder, findsOneWidget);
      
      expect(
        find.descendant(
          of: appBarFinder,
          matching: find.text('$app_name'),
        ),
        findsOneWidget,
      );
    });
  });
}
EOL

# Step 10: Run initial test
echo "✅ Running initial test..."
flutter test

# Step 11: Launch the app in Chrome
echo "🚀 Launching app in Chrome..."
flutter run -d chrome

# Step 12: Add backend functionality
echo "🔌 Step 12: Adding backend functionality..."
add_backend_dependencies
flutter pub get
create_backend_structure

echo "✅ Template setup complete!"
echo "The app is now running in Chrome. You can:"
echo "1. Press 'r' to hot reload"
echo "2. Press 'R' to hot restart"
echo "3. Press 'q' to quit"
