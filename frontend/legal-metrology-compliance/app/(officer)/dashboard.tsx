import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

function ActionCard({
  icon,
  title,
  description,
  onPress,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  description: string;
  onPress: () => void;
}) {
  return (
    <Pressable style={styles.actionCard} onPress={onPress}>
      <View style={styles.actionIcon}>
        <Ionicons name={icon} size={26} color="#111827" />
      </View>

      <View style={styles.actionContent}>
        <Text style={styles.actionTitle}>{title}</Text>
        <Text style={styles.actionDescription}>{description}</Text>
      </View>

      <Ionicons name="chevron-forward" size={22} color="#9CA3AF" />
    </Pressable>
  );
}

export default function DashboardScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Good Morning</Text>
            <Text style={styles.officerName}>Enforcement Officer</Text>
          </View>

          <View style={styles.profile}>
            <Ionicons name="person" size={22} color="#111827" />
          </View>
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>24</Text>
            <Text style={styles.statLabel}>Inspections</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statNumber}>08</Text>
            <Text style={styles.statLabel}>Violations</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statNumber}>16</Text>
            <Text style={styles.statLabel}>Compliant</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>New Inspection</Text>

        <ActionCard
          icon="camera-outline"
          title="Physical Package Scan"
          description="Capture and analyze package declarations"
          onPress={() => router.push("/(officer)/inspection")}
        />

        <ActionCard
          icon="globe-outline"
          title="E-Commerce Check"
          description="Analyze a product listing URL"
          onPress={() => router.push("/(officer)/ecommerce")}
        />

        <Text style={styles.sectionTitle}>Records</Text>

        <ActionCard
          icon="time-outline"
          title="Inspection History"
          description="View previous inspections and findings"
          onPress={() => router.push("/(officer)/history/index")}
        />

        <ActionCard
          icon="document-text-outline"
          title="Compliance Reports"
          description="View and export inspection reports"
          onPress={() => router.push("/(officer)/reports/index")}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },

  content: {
    padding: 20,
    paddingBottom: 40,
  },

  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 25,
  },

  greeting: {
    fontSize: 14,
    color: "#6B7280",
  },

  officerName: {
    fontSize: 23,
    fontWeight: "700",
    color: "#111827",
    marginTop: 3,
  },

  profile: {
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: "#E5E7EB",
    alignItems: "center",
    justifyContent: "center",
  },

  statsContainer: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 30,
  },

  statCard: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 15,
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },

  statNumber: {
    fontSize: 22,
    fontWeight: "700",
    color: "#111827",
  },

  statLabel: {
    fontSize: 11,
    color: "#6B7280",
    marginTop: 5,
  },

  sectionTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 12,
    marginTop: 5,
  },

  actionCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 15,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },

  actionIcon: {
    width: 50,
    height: 50,
    borderRadius: 12,
    backgroundColor: "#F3F4F6",
    alignItems: "center",
    justifyContent: "center",
  },

  actionContent: {
    flex: 1,
    marginLeft: 14,
  },

  actionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#111827",
  },

  actionDescription: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
});