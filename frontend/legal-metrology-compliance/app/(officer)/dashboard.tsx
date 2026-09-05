import React, {
  useEffect,
  useState,
} from "react";

import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";

import { useRouter } from "expo-router";

import {
  getCurrentOfficer,
  logoutOfficer,
  Officer,
} from "../../services/api";


export default function DashboardScreen() {

  const router = useRouter();

  const [officer, setOfficer] =
    useState<Officer | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  /*
  |--------------------------------------------------------------------------
  | Load Current Officer
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    loadOfficer();
  }, []);


  const loadOfficer = async () => {

    try {

      setLoading(true);

      setError("");

      const data =
        await getCurrentOfficer();

      setOfficer(data);

    } catch (error: any) {

      console.error(
        "Dashboard officer error:",
        error
      );

      setError(
        error.message ||
          "Unable to load officer information."
      );

    } finally {

      setLoading(false);

    }
  };


  /*
  |--------------------------------------------------------------------------
  | Logout
  |--------------------------------------------------------------------------
  */

  const handleLogout = () => {

    Alert.alert(
      "Logout",
      "Are you sure you want to logout?",
      [
        {
          text: "Cancel",
          style: "cancel",
        },

        {
          text: "Logout",
          style: "destructive",

          onPress: async () => {

            await logoutOfficer();

            router.replace(
              "/(auth)/login"
            );
          },
        },
      ]
    );
  };


  /*
  |--------------------------------------------------------------------------
  | Loading Screen
  |--------------------------------------------------------------------------
  */

  if (loading) {

    return (
      <View style={styles.loadingContainer}>

        <ActivityIndicator
          size="large"
          color="#1F4E79"
        />

        <Text style={styles.loadingText}>
          Loading officer profile...
        </Text>

      </View>
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Error Screen
  |--------------------------------------------------------------------------
  */

  if (error || !officer) {

    return (
      <View style={styles.errorContainer}>

        <Text style={styles.errorTitle}>
          Unable to Load Dashboard
        </Text>

        <Text style={styles.errorMessage}>
          {error ||
            "Officer information could not be loaded."}
        </Text>

        <TouchableOpacity
          style={styles.retryButton}
          onPress={loadOfficer}
        >

          <Text style={styles.retryButtonText}>
            Retry
          </Text>

        </TouchableOpacity>

        <TouchableOpacity
          style={styles.logoutErrorButton}
          onPress={handleLogout}
        >

          <Text style={styles.logoutErrorText}>
            Logout
          </Text>

        </TouchableOpacity>

      </View>
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Dashboard
  |--------------------------------------------------------------------------
  */

  return (

    <View style={styles.container}>

      {/* Header */}

      <View style={styles.header}>

        <View>

          <Text style={styles.headerTitle}>
            Legal Metrology
          </Text>

          <Text style={styles.headerSubtitle}>
            Compliance Management Platform
          </Text>

        </View>

        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >

          <Text style={styles.logoutButtonText}>
            Logout
          </Text>

        </TouchableOpacity>

      </View>


      <ScrollView
        contentContainerStyle={
          styles.scrollContent
        }
      >

        {/* Officer Profile */}

        <View style={styles.profileCard}>

          <View style={styles.profileIcon}>

            <Text style={styles.profileIconText}>
              {officer.full_name
                .charAt(0)
                .toUpperCase()}
            </Text>

          </View>

          <View style={styles.profileInfo}>

            <Text style={styles.welcomeText}>
              Welcome back
            </Text>

            <Text style={styles.officerName}>
              {officer.full_name}
            </Text>

            <Text style={styles.officerId}>
              Officer ID: {officer.officer_id}
            </Text>

            <View style={styles.roleBadge}>

              <Text style={styles.roleText}>
                {officer.role}
              </Text>

            </View>

          </View>

        </View>


        {/* Dashboard Title */}

        <Text style={styles.sectionTitle}>
          Inspection Dashboard
        </Text>


        {/* Statistics */}

        <View style={styles.statsContainer}>

          <View style={styles.statCard}>

            <Text style={styles.statNumber}>
              0
            </Text>

            <Text style={styles.statLabel}>
              Total Inspections
            </Text>

          </View>


          <View style={styles.statCard}>

            <Text style={styles.statNumber}>
              0
            </Text>

            <Text style={styles.statLabel}>
              Compliant
            </Text>

          </View>


          <View style={styles.statCard}>

            <Text style={styles.statNumber}>
              0
            </Text>

            <Text style={styles.statLabel}>
              Violations
            </Text>

          </View>

        </View>


        {/* Main Actions */}

        <Text style={styles.sectionTitle}>
          Inspection Actions
        </Text>


        <View style={styles.actionGrid}>


          {/* Physical Inspection */}

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() =>
              router.push(
                "/(officer)/inspection"
              )
            }
          >

            <View style={styles.actionIcon}>

              <Text style={styles.actionIconText}>
                📦
              </Text>

            </View>

            <Text style={styles.actionTitle}>
              Physical Inspection
            </Text>

            <Text style={styles.actionDescription}>
              Scan and analyze packaged
              commodity labels.
            </Text>

          </TouchableOpacity>


          {/* E-Commerce */}

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() =>
              router.push(
                "/(officer)/ecommerce"
              )
            }
          >

            <View style={styles.actionIcon}>

              <Text style={styles.actionIconText}>
                🌐
              </Text>

            </View>

            <Text style={styles.actionTitle}>
              E-Commerce Inspection
            </Text>

            <Text style={styles.actionDescription}>
              Analyze online product
              listings for compliance.
            </Text>

          </TouchableOpacity>


          {/* History */}

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() =>
              router.push(
                "/(officer)/history"
              )
            }
          >

            <View style={styles.actionIcon}>

              <Text style={styles.actionIconText}>
                📋
              </Text>

            </View>

            <Text style={styles.actionTitle}>
              Inspection History
            </Text>

            <Text style={styles.actionDescription}>
              View previous inspections
              and compliance findings.
            </Text>

          </TouchableOpacity>


          {/* Reports */}

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() =>
              router.push(
                "/(officer)/reports"
              )
            }
          >

            <View style={styles.actionIcon}>

              <Text style={styles.actionIconText}>
                📊
              </Text>

            </View>

            <Text style={styles.actionTitle}>
              Reports
            </Text>

            <Text style={styles.actionDescription}>
              Generate and review
              compliance reports.
            </Text>

          </TouchableOpacity>

        </View>


        {/* Officer Information */}

        <Text style={styles.sectionTitle}>
          Officer Information
        </Text>

        <View style={styles.infoCard}>

          <View style={styles.infoRow}>

            <Text style={styles.infoLabel}>
              Full Name
            </Text>

            <Text style={styles.infoValue}>
              {officer.full_name}
            </Text>

          </View>


          <View style={styles.divider} />


          <View style={styles.infoRow}>

            <Text style={styles.infoLabel}>
              Officer ID
            </Text>

            <Text style={styles.infoValue}>
              {officer.officer_id}
            </Text>

          </View>


          <View style={styles.divider} />


          <View style={styles.infoRow}>

            <Text style={styles.infoLabel}>
              Email
            </Text>

            <Text style={styles.infoValue}>
              {officer.email}
            </Text>

          </View>


          <View style={styles.divider} />


          <View style={styles.infoRow}>

            <Text style={styles.infoLabel}>
              Role
            </Text>

            <Text style={styles.infoValue}>
              {officer.role}
            </Text>

          </View>


          <View style={styles.divider} />


          <View style={styles.infoRow}>

            <Text style={styles.infoLabel}>
              Account Status
            </Text>

            <Text
              style={[
                styles.infoValue,
                styles.activeStatus,
              ]}
            >
              {officer.is_active
                ? "Active"
                : "Inactive"}
            </Text>

          </View>

        </View>


        {/* Footer */}

        <View style={styles.footer}>

          <Text style={styles.footerText}>
            Legal Metrology Compliance Platform
          </Text>

          <Text style={styles.footerSubText}>
            AI-assisted compliance inspection
            and evidence management
          </Text>

        </View>

      </ScrollView>

    </View>
  );
}


/*
|--------------------------------------------------------------------------
| Styles
|--------------------------------------------------------------------------
*/

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#F4F6F8",
  },

  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F4F6F8",
  },

  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: "#6B7280",
  },

  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 30,
    backgroundColor: "#F4F6F8",
  },

  errorTitle: {
    fontSize: 22,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 10,
    textAlign: "center",
  },

  errorMessage: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 24,
  },

  retryButton: {
    backgroundColor: "#1F4E79",
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
  },

  retryButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "600",
  },

  logoutErrorButton: {
    marginTop: 12,
    paddingHorizontal: 30,
    paddingVertical: 12,
  },

  logoutErrorText: {
    color: "#B91C1C",
    fontSize: 14,
    fontWeight: "600",
  },

  header: {
    backgroundColor: "#1F4E79",
    paddingHorizontal: 20,
    paddingTop: 55,
    paddingBottom: 18,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  headerTitle: {
    color: "#FFFFFF",
    fontSize: 21,
    fontWeight: "700",
  },

  headerSubtitle: {
    color: "#D9E7F5",
    fontSize: 11,
    marginTop: 4,
  },

  logoutButton: {
    borderWidth: 1,
    borderColor: "#FFFFFF",
    borderRadius: 7,
    paddingHorizontal: 13,
    paddingVertical: 8,
  },

  logoutButtonText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "600",
  },

  scrollContent: {
    padding: 18,
    paddingBottom: 40,
  },

  profileCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 20,
    flexDirection: "row",
    alignItems: "center",
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    marginBottom: 24,
  },

  profileIcon: {
    width: 62,
    height: 62,
    borderRadius: 31,
    backgroundColor: "#E5EEF7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 16,
  },

  profileIconText: {
    fontSize: 25,
    fontWeight: "700",
    color: "#1F4E79",
  },

  profileInfo: {
    flex: 1,
  },

  welcomeText: {
    fontSize: 12,
    color: "#6B7280",
  },

  officerName: {
    fontSize: 20,
    fontWeight: "700",
    color: "#1F2937",
    marginTop: 2,
  },

  officerId: {
    fontSize: 13,
    color: "#6B7280",
    marginTop: 4,
  },

  roleBadge: {
    alignSelf: "flex-start",
    marginTop: 8,
    paddingHorizontal: 9,
    paddingVertical: 4,
    borderRadius: 5,
    backgroundColor: "#E8F1F8",
  },

  roleText: {
    fontSize: 10,
    fontWeight: "700",
    color: "#1F4E79",
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 12,
    marginTop: 4,
  },

  statsContainer: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 26,
  },

  statCard: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 10,
    padding: 16,
    alignItems: "center",
    elevation: 2,
  },

  statNumber: {
    fontSize: 24,
    fontWeight: "700",
    color: "#1F4E79",
  },

  statLabel: {
    fontSize: 11,
    color: "#6B7280",
    textAlign: "center",
    marginTop: 5,
  },

  actionGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 24,
  },

  actionCard: {
    width: "48%",
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.05,
    shadowRadius: 5,
  },

  actionIcon: {
    width: 42,
    height: 42,
    borderRadius: 9,
    backgroundColor: "#EAF1F7",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 10,
  },

  actionIconText: {
    fontSize: 21,
  },

  actionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 6,
  },

  actionDescription: {
    fontSize: 11,
    color: "#6B7280",
    lineHeight: 16,
  },

  infoCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    paddingHorizontal: 18,
    marginBottom: 25,
    elevation: 2,
  },

  infoRow: {
    paddingVertical: 14,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  infoLabel: {
    fontSize: 13,
    color: "#6B7280",
  },

  infoValue: {
    fontSize: 13,
    fontWeight: "600",
    color: "#1F2937",
    maxWidth: "60%",
    textAlign: "right",
  },

  activeStatus: {
    color: "#15803D",
  },

  divider: {
    height: 1,
    backgroundColor: "#E5E7EB",
  },

  footer: {
    alignItems: "center",
    marginTop: 5,
  },

  footerText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#6B7280",
  },

  footerSubText: {
    fontSize: 10,
    color: "#9CA3AF",
    marginTop: 4,
    textAlign: "center",
  },

});