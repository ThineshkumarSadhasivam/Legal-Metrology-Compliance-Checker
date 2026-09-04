import { StyleSheet, Text, View } from "react-native";

export default function InspectionResultScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Inspection Result</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: "center", justifyContent: "center" },
  title: { fontSize: 24, fontWeight: "700" },
});
