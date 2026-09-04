import { SafeAreaView, StyleSheet, Text, View } from "react-native";

export default function ReportsScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Compliance Reports</Text>
        <Text style={styles.subtitle}>
          Generated reports will appear here.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8FAFC" },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  title: { fontSize: 24, fontWeight: "700" },
  subtitle: { color: "#6B7280", marginTop: 8 },
});