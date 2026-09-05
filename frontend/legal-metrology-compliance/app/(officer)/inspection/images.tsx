import React, { useEffect, useState } from "react";

import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Image,
  ScrollView,
  ActivityIndicator,
} from "react-native";

import * as ImagePicker from "expo-image-picker";
import { router, useLocalSearchParams } from "expo-router";

import {
  uploadInspectionImage,
  getInspectionImages,
} from "../../../services/api";

// ======================================================
// TYPES
// ======================================================

interface UploadedImage {
  id: number;
  inspection_id: number;
  inspection_number?: string;
  image_type: string;
  file_name: string;
  file_path?: string;
  mime_type?: string;
  file_size?: number;
  uploaded_at?: string;
}

// ======================================================
// IMAGE TYPES
// ======================================================

const IMAGE_TYPES = [
  "FRONT",
  "BACK",
  "SIDE",
  "LABEL",
  "PDP",
];

// ======================================================
// SCREEN
// ======================================================

export default function InspectionImagesScreen() {

  const { id } = useLocalSearchParams();

  const inspectionId = Number(id);

  // ----------------------------------------------------
  // STATE
  // ----------------------------------------------------

  const [selectedImage, setSelectedImage] =
    useState<string | null>(null);

  const [imageType, setImageType] =
    useState("FRONT");

  const [uploading, setUploading] =
    useState(false);

  const [loadingImages, setLoadingImages] =
    useState(true);

  const [uploadedImages, setUploadedImages] =
    useState<UploadedImage[]>([]);

  const [hasUploadedImage, setHasUploadedImage] =
    useState(false);

  // ====================================================
  // LOAD IMAGES
  // ====================================================

  const loadImages = async () => {

    if (!inspectionId) {
      return;
    }

    try {

      setLoadingImages(true);

      console.log(
        "Loading images for inspection:",
        inspectionId
      );

      const result =
        await getInspectionImages(
          inspectionId
        );

      console.log(
        "DATABASE IMAGES:",
        result.images
      );

      setUploadedImages(
        result.images || []
      );

      setHasUploadedImage(
        (result.images || []).length > 0
      );

    } catch (error) {

      console.error(
        "LOAD IMAGES ERROR:",
        error
      );

    } finally {

      setLoadingImages(false);

    }
  };

  // ====================================================
  // INITIAL LOAD
  // ====================================================

  useEffect(() => {

    loadImages();

  }, [inspectionId]);

  // ====================================================
  // CHECK UPLOADED TYPE
  // ====================================================

  const isUploaded = (
    type: string
  ) => {

    return uploadedImages.some(
      image =>
        image.image_type === type
    );

  };

  // ====================================================
  // FIND NEXT TYPE
  // ====================================================

  const findNextType = (
    images: UploadedImage[]
  ) => {

    return (
      IMAGE_TYPES.find(
        type =>
          !images.some(
            image =>
              image.image_type === type
          )
      ) || "FRONT"
    );

  };

  const requiredImageTypes = IMAGE_TYPES;

  const hasCompletedRequiredImages = (
    images: UploadedImage[]
  ) =>
    requiredImageTypes.every(type =>
      images.some(image => image.image_type === type)
    );

  // ====================================================
  // CAMERA
  // ====================================================

  const takePhoto = async () => {

    try {

      console.log(
        "OPENING CAMERA"
      );

      console.log(
        "Current image type:",
        imageType
      );

      const permission =
        await ImagePicker.requestCameraPermissionsAsync();

      if (!permission.granted) {

        Alert.alert(
          "Camera Permission",
          "Camera permission is required to capture inspection images."
        );

        return;
      }

      const result =
        await ImagePicker.launchCameraAsync({
          mediaTypes: ["images"],
          quality: 0.9,
        });

      if (result.canceled) {

        console.log(
          "Camera cancelled"
        );

        return;
      }

      const uri =
        result.assets[0].uri;

      console.log(
        "CAMERA IMAGE:",
        uri
      );

      setSelectedImage(uri);

    } catch (error) {

      console.error(
        "CAMERA ERROR:",
        error
      );

      Alert.alert(
        "Camera Error",
        "Unable to open camera."
      );

    }
  };

  // ====================================================
  // GALLERY
  // ====================================================

  const pickFromGallery = async () => {

    try {

      console.log(
        "OPENING GALLERY"
      );

      console.log(
        "Current image type:",
        imageType
      );

      const permission =
        await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (!permission.granted) {

        Alert.alert(
          "Gallery Permission",
          "Gallery permission is required to select an inspection image."
        );

        return;
      }

      const result =
        await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ["images"],
          quality: 0.9,
        });

      if (result.canceled) {

        console.log(
          "Gallery cancelled"
        );

        return;
      }

      const uri =
        result.assets[0].uri;

      console.log(
        "GALLERY IMAGE:",
        uri
      );

      setSelectedImage(uri);

    } catch (error) {

      console.error(
        "GALLERY ERROR:",
        error
      );

      Alert.alert(
        "Gallery Error",
        "Unable to open gallery."
      );

    }
  };

  // ====================================================
  // UPLOAD
  // ====================================================

  const handleUpload = async () => {

    if (uploading) {
      return;
    }

    if (!selectedImage) {

      Alert.alert(
        "No Image",
        "Please capture or select an image first."
      );

      return;
    }

    if (!inspectionId) {

      Alert.alert(
        "Invalid Inspection",
        "Inspection ID is missing."
      );

      return;
    }

    try {

      setUploading(true);

      const currentType =
        imageType;

      const currentImage =
        selectedImage;

      console.log(
        "================================="
      );

      console.log(
        "STARTING IMAGE UPLOAD"
      );

      console.log(
        "Inspection ID:",
        inspectionId
      );

      console.log(
        "Image Type:",
        currentType
      );

      console.log(
        "Image URI:",
        currentImage
      );

      console.log(
        "================================="
      );

      // ------------------------------------------------
      // UPLOAD
      // ------------------------------------------------

      const uploaded =
        await uploadInspectionImage(
          inspectionId,
          currentImage,
          currentType
        );

      console.log(
        "IMAGE UPLOADED SUCCESSFULLY:",
        uploaded
      );

      // Keep the next-upload action available immediately after the POST.
      setUploadedImages(previousImages => [
        uploaded,
        ...previousImages.filter(
          image => image.id !== uploaded.id
        ),
      ]);

      setHasUploadedImage(true);

      // ------------------------------------------------
      // CLEAR CURRENT IMAGE
      // ------------------------------------------------

      setSelectedImage(null);

      // ------------------------------------------------
      // GET FRESH DATA FROM SERVER
      // ------------------------------------------------

      let latestImages = [
        uploaded,
        ...uploadedImages.filter(
          image => image.id !== uploaded.id
        ),
      ];

      try {
        const result =
          await getInspectionImages(
            inspectionId
          );

        latestImages = result.images || [];

        console.log(
          "LATEST SERVER IMAGES:",
          latestImages
        );

        setUploadedImages(
          latestImages
        );
      } catch (refreshError) {
        console.warn(
          "Image uploaded, but the image list could not refresh:",
          refreshError
        );
      }

      // ------------------------------------------------
      // DETERMINE NEXT TYPE
      // ------------------------------------------------

      const nextType =
        findNextType(
          latestImages
        );

      if (hasCompletedRequiredImages(latestImages)) {
        router.replace({
          pathname: "/(officer)/inspection/complete",
          params: {
            id: String(inspectionId),
            count: String(latestImages.length),
          },
        });
        return;
      }

      console.log(
        "NEXT IMAGE TYPE:",
        nextType
      );

      setImageType(
        nextType
      );

      // ------------------------------------------------
      // SUCCESS
      // ------------------------------------------------

      Alert.alert(
        "Image Uploaded",
        `${currentType} image uploaded successfully.\n\n` +
        `Inspection: LM-${String(
          inspectionId
        ).padStart(5, "0")}\n\n` +
        `Next image: ${nextType}`
      );

    } catch (error: any) {

      console.error(
        "UPLOAD ERROR:",
        error
      );

      Alert.alert(
        "Upload Failed",
        error?.message ||
        "Unable to upload image."
      );

    } finally {

      setUploading(false);

    }
  };

  // ====================================================
  // SELECT TYPE
  // ====================================================

  const selectImageType = (
    type: string
  ) => {
    setImageType(type);

    // Important:
    // Remove any image selected for the previous type
    setSelectedImage(null);
  };

  // ====================================================
  // UI
  // ====================================================

  return (

    <ScrollView
      contentContainerStyle={
        styles.container
      }
    >

      {/* HEADER */}

      <Text style={styles.title}>
        Product Inspection
      </Text>

      <Text style={styles.inspectionText}>
        Inspection ID: {inspectionId}
      </Text>

      {/* INFO */}

      <View style={styles.infoCard}>

        <Text style={styles.infoTitle}>
          Same Product • Same Inspection
        </Text>

        <Text style={styles.infoText}>
          Capture multiple views of the same
          package. All images are linked to
          this inspection.
        </Text>

      </View>

      {/* COUNTER */}

      <View style={styles.counterCard}>

        <View>

          <Text style={styles.counterLabel}>
            Images Uploaded
          </Text>

          <Text style={styles.counterValue}>
            {uploadedImages.length}
          </Text>

        </View>

        <View>

          <Text style={styles.counterLabel}>
            Inspection
          </Text>

          <Text style={styles.counterInspection}>
            LM-{String(
              inspectionId
            ).padStart(5, "0")}
          </Text>

        </View>

      </View>

      {/* IMAGE TYPE */}

      <Text style={styles.sectionTitle}>
        Select Image Type
      </Text>

      <View style={styles.typeContainer}>

        {IMAGE_TYPES.map(type => {

          const uploaded =
            isUploaded(type);

          const selected =
            imageType === type;

          return (

            <TouchableOpacity
              key={type}

              style={[
                styles.typeButton,

                selected &&
                  styles.selectedType,

                uploaded &&
                  styles.uploadedType,
              ]}

              onPress={() =>
                selectImageType(type)
              }

              disabled={uploading}
            >

              <Text
                style={[
                  styles.typeText,

                  selected &&
                    styles.selectedTypeText,
                ]}
              >

                {uploaded
                  ? "✓ "
                  : ""}

                {type}

              </Text>

            </TouchableOpacity>

          );

        })}

      </View>

      {/* CURRENT IMAGE */}

      <View style={styles.currentTypeCard}>

        <View>

          <Text style={styles.currentTypeLabel}>
            Ready to capture
          </Text>

          <Text style={styles.currentTypeValue}>
            {imageType}
          </Text>

        </View>

        <Text style={styles.cameraIcon}>
          📷
        </Text>

      </View>

      <Text style={styles.requirementText}>
        All five views are required: {requiredImageTypes.join(" / ")}
      </Text>

      {/* =================================================
          CAPTURE BUTTON
          ================================================= */}

      <TouchableOpacity
        style={[
          styles.primaryButton,
          uploading &&
            styles.disabledButton,
        ]}

        onPress={takePhoto}

        disabled={uploading}
      >

        <Text style={styles.buttonText}>
          📷 Capture {imageType}
        </Text>

      </TouchableOpacity>

      {/* =================================================
          GALLERY BUTTON
          ================================================= */}

      <TouchableOpacity
        style={[
          styles.secondaryButton,
          uploading &&
            styles.disabledButton,
        ]}

        onPress={pickFromGallery}

        disabled={uploading}
      >

        <Text style={styles.secondaryButtonText}>
          🖼 Select {imageType} from Gallery
        </Text>

      </TouchableOpacity>

      <TouchableOpacity
        style={styles.nextImageButton}
        onPress={() => {
          setSelectedImage(null);
          setImageType("FRONT");
        }}
        disabled={uploading}
      >
        <Text style={styles.nextImageButtonText}>
          {hasUploadedImage
            ? "+ Capture another image for this inspection"
            : "+ Add another image to this inspection"}
        </Text>
      </TouchableOpacity>

      {/* =================================================
          PREVIEW
          ================================================= */}

      {selectedImage !== null && (

        <View style={styles.previewCard}>

          <Text style={styles.previewTitle}>
            Preview — {imageType}
          </Text>

          <Image
            source={{
              uri: selectedImage,
            }}

            style={styles.preview}

            resizeMode="contain"
          />

          <TouchableOpacity
            style={[
              styles.uploadButton,
              uploading &&
                styles.disabledButton,
            ]}

            onPress={handleUpload}

            disabled={uploading}
          >

            {uploading ? (

              <View
                style={
                  styles.loadingContainer
                }
              >

                <ActivityIndicator
                  color="#FFFFFF"
                />

                <Text style={styles.buttonText}>
                  Uploading...
                </Text>

              </View>

            ) : (

              <Text style={styles.buttonText}>
                Upload {imageType}
              </Text>

            )}

          </TouchableOpacity>

        </View>

      )}

      {/* =================================================
          UPLOADED IMAGES
          ================================================= */}

      <View style={styles.uploadedSection}>

        <Text style={styles.sectionTitle}>
          Images Stored for This Inspection
        </Text>

        {loadingImages ? (

          <ActivityIndicator
            color="#1F4E79"
          />

        ) : uploadedImages.length === 0 ? (

          <View style={styles.emptyCard}>

            <Text style={styles.emptyText}>
              No images uploaded yet.
            </Text>

          </View>

        ) : (

          uploadedImages.map(
            (image, index) => (

              <View
                key={image.id}
                style={styles.imageRow}
              >

                <View
                  style={styles.imageNumber}
                >

                  <Text
                    style={
                      styles.imageNumberText
                    }
                  >
                    {index + 1}
                  </Text>

                </View>

                <View
                  style={styles.imageInfo}
                >

                  <Text
                    style={styles.imageTypeText}
                  >
                    {image.image_type}
                  </Text>

                  <Text
                    style={styles.fileNameText}
                    numberOfLines={1}
                  >
                    {image.file_name}
                  </Text>

                </View>

                <Text
                  style={
                    styles.uploadedStatus
                  }
                >
                  ✓
                </Text>

              </View>

            )
          )

        )}

      </View>

      {/* =================================================
          ANALYZE
          ================================================= */}

      {uploadedImages.length > 0 && (

        <TouchableOpacity
          style={styles.analyzeButton}

          onPress={() => {

            Alert.alert(
              "Ready for Analysis",

              `Inspection #${inspectionId}\n\n` +
              `${uploadedImages.length} image(s) ` +
              `are stored for this product.\n\n` +
              `All images will be processed together ` +
              `by the OCR and compliance engine.`
            );

          }}
        >

          <Text
            style={
              styles.analyzeButtonText
            }
          >
            🔍 Analyze Product
          </Text>

        </TouchableOpacity>

      )}

    </ScrollView>
  );
}

// ======================================================
// STYLES
// ======================================================

const styles = StyleSheet.create({

  container: {
    flexGrow: 1,
    padding: 24,
    backgroundColor: "#F4F6F8",
  },

  title: {
    fontSize: 26,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 6,
  },

  inspectionText: {
    fontSize: 14,
    color: "#6B7280",
    marginBottom: 18,
  },

  infoCard: {
    backgroundColor: "#EAF2F8",
    borderRadius: 12,
    padding: 15,
    marginBottom: 18,
  },

  infoTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#1F4E79",
    marginBottom: 5,
  },

  infoText: {
    fontSize: 13,
    lineHeight: 19,
    color: "#374151",
  },

  counterCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 18,
    marginBottom: 25,
    flexDirection: "row",
    justifyContent: "space-between",
  },

  counterLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 4,
  },

  counterValue: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1F4E79",
  },

  counterInspection: {
    fontSize: 18,
    fontWeight: "700",
    color: "#166534",
  },

  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 12,
  },

  typeContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 15,
  },

  typeButton: {
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: "#FFFFFF",
  },

  selectedType: {
    backgroundColor: "#1F4E79",
    borderColor: "#1F4E79",
  },

  uploadedType: {
    borderColor: "#166534",
  },

  typeText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#374151",
  },

  selectedTypeText: {
    color: "#FFFFFF",
  },

  currentTypeCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 10,
    padding: 14,
    marginBottom: 15,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#DDE3E8",
  },

  currentTypeLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 3,
  },

  currentTypeValue: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1F4E79",
  },

  requirementText: {
    color: "#6B7280",
    fontSize: 12,
    marginBottom: 15,
  },

  cameraIcon: {
    fontSize: 26,
  },

  primaryButton: {
    height: 52,
    borderRadius: 9,
    backgroundColor: "#1F4E79",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },

  secondaryButton: {
    height: 52,
    borderRadius: 9,
    borderWidth: 1,
    borderColor: "#1F4E79",
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 24,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "600",
  },

  secondaryButtonText: {
    color: "#1F4E79",
    fontSize: 15,
    fontWeight: "600",
  },

  previewCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 15,
    marginBottom: 25,
  },

  previewTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1F2937",
    marginBottom: 12,
  },

  preview: {
    width: "100%",
    height: 300,
    borderRadius: 8,
    backgroundColor: "#F3F4F6",
    marginBottom: 15,
  },

  uploadButton: {
    height: 50,
    borderRadius: 9,
    backgroundColor: "#166534",
    justifyContent: "center",
    alignItems: "center",
  },

  disabledButton: {
    opacity: 0.45,
  },

  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },

  uploadedSection: {
    marginBottom: 20,
  },

  emptyCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 20,
    alignItems: "center",
  },

  emptyText: {
    fontSize: 14,
    color: "#6B7280",
  },

  imageRow: {
    backgroundColor: "#FFFFFF",
    borderRadius: 10,
    padding: 13,
    marginBottom: 8,
    flexDirection: "row",
    alignItems: "center",
  },

  imageNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "#EAF2F8",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  imageNumberText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#1F4E79",
  },

  imageInfo: {
    flex: 1,
  },

  imageTypeText: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1F2937",
  },

  fileNameText: {
    fontSize: 11,
    color: "#9CA3AF",
    marginTop: 2,
  },

  uploadedStatus: {
    fontSize: 20,
    fontWeight: "700",
    color: "#166534",
  },

  analyzeButton: {
    height: 56,
    borderRadius: 10,
    backgroundColor: "#7C3AED",
    justifyContent: "center",
    alignItems: "center",
    marginTop: 5,
    marginBottom: 20,
  },

  analyzeButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },

  nextImageButton: {
    height: 52,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#1F4E79",
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },

  nextImageButtonText: {
    color: "#1F4E79",
    fontSize: 15,
    fontWeight: "700",
  },

});