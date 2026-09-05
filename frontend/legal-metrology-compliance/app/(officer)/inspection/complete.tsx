import { Ionicons } from "@expo/vector-icons";
import { router, useLocalSearchParams } from "expo-router";
import {
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";

export default function InspectionCompleteScreen() {
  const { id, count } = useLocalSearchParams();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconCircle}>
          <Ionicons name="checkmark" size={42} color="#FFFFFF" />
        </View>
        <Text style={styles.title}>Images uploaded</Text>
        <Text style={styles.description}>
          Inspection {id} is ready for compliance analysis.
        </Text>
        <Text style={styles.count}>{count} image(s) stored</Text>
        <Pressable
          style={styles.button}
          onPress={() => router.replace("/(officer)/dashboard")}
        >
          <Text style={styles.buttonText}>Return to dashboard</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8FAFC" },
  content: {
    alignItems: "center",
    flex: 1,
    justifyContent: "center",
    padding: 28,
  },
  iconCircle: {
    alignItems: "center",
    backgroundColor: "#15803D",
    borderRadius: 42,
    height: 84,
    justifyContent: "center",
    width: 84,
  },
  title: { color: "#111827", fontSize: 27, fontWeight: "700", marginTop: 22 },
  description: { color: "#6B7280", fontSize: 15, marginTop: 10, textAlign: "center" },
  count: { color: "#15803D", fontSize: 15, fontWeight: "700", marginTop: 14 },
  button: {
    alignItems: "center",
    backgroundColor: "#111827",
    borderRadius: 10,
    justifyContent: "center",
    marginTop: 30,
    minHeight: 52,
    paddingHorizontal: 24,
  },
  buttonText: { color: "#FFFFFF", fontSize: 15, fontWeight: "700" },
});