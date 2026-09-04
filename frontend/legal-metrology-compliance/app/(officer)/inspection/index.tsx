import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";

export default function InspectionScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="camera-outline" size={70} color="#111827" />

        <Text style={styles.title}>Physical Package Inspection</Text>

        <Text style={styles.description}>
          Capture package images for Legal Metrology compliance analysis.
        </Text>

        <Pressable
          style={styles.button}
          onPress={() => router.push("/(officer)/inspection/result")}
        >
          <Ionicons name="camera" size={20} color="#FFFFFF" />
          <Text style={styles.buttonText}>Start Scan</Text>
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
    alignItems: "center",
    justifyContent: "center",
    padding: 30,
  },

  title: {
    fontSize: 23,
    fontWeight: "700",
    color: "#111827",
    marginTop: 20,
    textAlign: "center",
  },

  description: {
    color: "#6B7280",
    textAlign: "center",
    marginTop: 10,
    lineHeight: 21,
  },

  button: {
    marginTop: 30,
    backgroundColor: "#111827",
    borderRadius: 12,
    paddingHorizontal: 25,
    paddingVertical: 15,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },

  buttonText: {
    color: "#FFFFFF",
    fontWeight: "700",
  },
});