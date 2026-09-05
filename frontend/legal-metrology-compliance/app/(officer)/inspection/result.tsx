import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { router } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  Image,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import {
  createInspection,
  uploadInspectionImage,
} from "../../../services/api";

export default function InspectionResultScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [inspectionNumber, setInspectionNumber] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  const capturePackage = async () => {
    setError("");
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      setError("Camera permission is required to scan a package.");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
      quality: 0.8,
      allowsEditing: false,
    });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
    }
  };

  const saveInspection = async () => {
    if (!imageUri) {
      setError("Capture a package image before saving the scan.");
      return;
    }

    setError("");
    setIsSaving(true);
    try {
      const inspection = await createInspection("PHYSICAL");
      await uploadInspectionImage(inspection.id, imageUri, "FRONT");
      setInspectionNumber(inspection.inspection_number);
      router.replace({
        pathname: "/(officer)/inspection/images",
        params: { id: String(inspection.id) },
      });
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Unable to save the inspection."
      );
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={22} color="#111827" />
          </Pressable>
          <View>
            <Text style={styles.eyebrow}>PHYSICAL INSPECTION</Text>
            <Text style={styles.title}>Scan package</Text>
          </View>
        </View>

        <Text style={styles.description}>
          Capture the package front and save its inspection record.
        </Text>

        <Pressable style={styles.captureArea} onPress={capturePackage}>
          {imageUri ? (
            <Image source={{ uri: imageUri }} style={styles.preview} />
          ) : (
            <>
              <Ionicons name="camera-outline" size={42} color="#2563EB" />
              <Text style={styles.captureTitle}>Capture package</Text>
              <Text style={styles.captureHint}>Tap to open the camera</Text>
            </>
          )}
        </Pressable>

        {error ? <Text style={styles.error}>{error}</Text> : null}
        {inspectionNumber ? (
          <View style={styles.successBox}>
            <Ionicons name="checkmark-circle" size={22} color="#15803D" />
            <View>
              <Text style={styles.successTitle}>Scan saved</Text>
              <Text style={styles.successText}>{inspectionNumber}</Text>
            </View>
          </View>
        ) : (
          <Pressable
            style={[styles.saveButton, isSaving && styles.disabled]}
            onPress={saveInspection}
            disabled={isSaving}
          >
            {isSaving ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Ionicons name="cloud-upload-outline" size={20} color="#FFFFFF" />
            )}
            <Text style={styles.saveText}>
              {isSaving ? "Saving scan..." : "Save inspection"}
            </Text>
          </Pressable>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8FAFC" },
  content: { padding: 24, paddingBottom: 40 },
  header: { flexDirection: "row", alignItems: "center", gap: 14 },
  backButton: { padding: 4 },
  eyebrow: { color: "#2563EB", fontSize: 11, fontWeight: "700", letterSpacing: 1 },
  title: { color: "#111827", fontSize: 26, fontWeight: "700", marginTop: 3 },
  description: { color: "#6B7280", fontSize: 15, lineHeight: 22, marginTop: 16 },
  captureArea: {
    alignItems: "center", aspectRatio: 1.45, backgroundColor: "#EFF6FF",
    borderColor: "#BFDBFE", borderRadius: 14, borderWidth: 1,
    justifyContent: "center", marginTop: 24, overflow: "hidden",
  },
  preview: { height: "100%", width: "100%" },
  captureTitle: { color: "#1D4ED8", fontSize: 17, fontWeight: "700", marginTop: 10 },
  captureHint: { color: "#64748B", fontSize: 13, marginTop: 5 },
  error: { color: "#B91C1C", fontSize: 13, marginTop: 14 },
  saveButton: {
    alignItems: "center", backgroundColor: "#111827", borderRadius: 11,
    flexDirection: "row", gap: 9, justifyContent: "center", marginTop: 24, minHeight: 52,
  },
  saveText: { color: "#FFFFFF", fontSize: 15, fontWeight: "700" },
  disabled: { opacity: 0.65 },
  successBox: {
    alignItems: "center", backgroundColor: "#F0FDF4", borderColor: "#BBF7D0",
    borderRadius: 11, borderWidth: 1, flexDirection: "row", gap: 10, marginTop: 24, padding: 14,
  },
  successTitle: { color: "#166534", fontSize: 15, fontWeight: "700" },
  successText: { color: "#15803D", fontSize: 13, marginTop: 2 },
});
