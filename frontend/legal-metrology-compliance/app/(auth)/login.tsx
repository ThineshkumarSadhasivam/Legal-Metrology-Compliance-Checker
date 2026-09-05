import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import * as SecureStore from "expo-secure-store";

import { loginOfficer } from "../../services/api";

export default function LoginScreen() {
  const router = useRouter();

  const [officerId, setOfficerId] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    // Basic validation
    if (!officerId.trim() || !password.trim()) {
      setError("Please enter Officer ID and password.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      // Send login request to FastAPI
      const data = await loginOfficer(
        officerId.trim(),
        password
      );

      console.log("Login successful:", data);

      // Store JWT securely
      await SecureStore.setItemAsync(
        "access_token",
        data.access_token
      );

      await SecureStore.setItemAsync(
        "officer_id",
        data.officer_id
      );

      await SecureStore.setItemAsync(
        "role",
        data.role
      );

      // Navigate to officer dashboard
      router.replace("/(officer)/dashboard");

    } catch (err: any) {
      console.error("Login error:", err);

      if (err.message) {
        setError(err.message);
      } else {
        setError(
          "Unable to connect to server. Please check your connection."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={
        Platform.OS === "ios" ? "padding" : undefined
      }
    >
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.card}>

          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>
              Legal Metrology
            </Text>

            <Text style={styles.subtitle}>
              Compliance Management Platform
            </Text>
          </View>

          {/* Login Section */}
          <View style={styles.form}>

            <Text style={styles.formTitle}>
              Officer Login
            </Text>

            <Text style={styles.label}>
              Officer ID
            </Text>

            <TextInput
              style={styles.input}
              placeholder="Enter Officer ID"
              placeholderTextColor="#999"
              value={officerId}
              onChangeText={(text) => {
                setOfficerId(text);
                setError("");
              }}
              autoCapitalize="characters"
              autoCorrect={false}
              editable={!loading}
            />

            <Text style={styles.label}>
              Password
            </Text>

            <TextInput
              style={styles.input}
              placeholder="Enter password"
              placeholderTextColor="#999"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                setError("");
              }}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading}
            />

            {/* Error Message */}
            {error ? (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>
                  {error}
                </Text>
              </View>
            ) : null}

            {/* Login Button */}
            <TouchableOpacity
              style={[
                styles.loginButton,
                loading && styles.loginButtonDisabled,
              ]}
              onPress={handleLogin}
              disabled={loading}
              activeOpacity={0.8}
            >
              {loading ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator
                    size="small"
                    color="#FFFFFF"
                  />

                  <Text style={styles.loginButtonText}>
                    Signing in...
                  </Text>
                </View>
              ) : (
                <Text style={styles.loginButtonText}>
                  Sign In
                </Text>
              )}
            </TouchableOpacity>

          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Authorized Enforcement Personnel Only
            </Text>

            <Text style={styles.versionText}>
              Legal Metrology Compliance Platform
            </Text>
          </View>

        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F4F6F8",
  },

  scrollContainer: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },

  card: {
    width: "100%",
    maxWidth: 450,
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 28,

    // Shadow - iOS
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,

    // Shadow - Android
    elevation: 5,
  },

  header: {
    alignItems: "center",
    marginBottom: 35,
  },

  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1F2937",
    textAlign: "center",
  },

  subtitle: {
    marginTop: 8,
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
  },

  form: {
    width: "100%",
  },

  formTitle: {
    fontSize: 20,
    fontWeight: "600",
    color: "#1F2937",
    marginBottom: 24,
  },

  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 8,
  },

  input: {
    height: 50,
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 8,
    paddingHorizontal: 14,
    fontSize: 15,
    color: "#111827",
    backgroundColor: "#FFFFFF",
    marginBottom: 18,
  },

  errorContainer: {
    backgroundColor: "#FEF2F2",
    borderWidth: 1,
    borderColor: "#FECACA",
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },

  errorText: {
    color: "#B91C1C",
    fontSize: 13,
    lineHeight: 18,
  },

  loginButton: {
    height: 50,
    borderRadius: 8,
    backgroundColor: "#1F4E79",
    justifyContent: "center",
    alignItems: "center",
    marginTop: 4,
  },

  loginButtonDisabled: {
    opacity: 0.7,
  },

  loginButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },

  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },

  footer: {
    alignItems: "center",
    marginTop: 30,
  },

  footerText: {
    fontSize: 12,
    color: "#6B7280",
    textAlign: "center",
  },

  versionText: {
    fontSize: 11,
    color: "#9CA3AF",
    marginTop: 6,
    textAlign: "center",
  },
});