import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

export default function EcommerceScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="globe-outline" size={60} color="#111827" />

        <Text style={styles.title}>E-Commerce Compliance</Text>

        <Text style={styles.description}>
          Enter a specific product listing URL to analyze available product
          information and images.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="https://example.com/product"
          placeholderTextColor="#9CA3AF"
          autoCapitalize="none"
          keyboardType="url"
        />

        <Pressable
          style={styles.button}
          onPress={() => router.push("/(officer)/ecommerce/result")}
        >
          <Text style={styles.buttonText}>Analyze Listing</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },

  content: {
    flex: 1,
    padding: 25,
    justifyContent: "center",
  },

  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#111827",
    marginTop: 20,
  },

  description: {
    color: "#6B7280",
    lineHeight: 21,
    marginTop: 10,
    marginBottom: 25,
  },

  input: {
    height: 54,
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 12,
    backgroundColor: "#FFFFFF",
    paddingHorizontal: 15,
    fontSize: 14,
  },

  button: {
    height: 54,
    backgroundColor: "#111827",
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 15,
  },

  buttonText: {
    color: "#FFFFFF",
    fontWeight: "700",
  },
});