import * as SecureStore from "expo-secure-store";
import * as FileSystem from "expo-file-system/legacy";
import { Platform } from "react-native";

import { API_BASE_URL } from "../constants/config";

import type {
  InspectionResponse,
} from "../types/inspection";


// ======================================================
// TYPES
// ======================================================

export interface LoginResponse {
  access_token: string;
  token_type: string;
  officer_id: string;
  role: string;
}

export interface Officer {
  id: number;
  officer_id: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface InspectionImage {
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

export interface InspectionImagesResponse {
  inspection_id: number;
  inspection_number: string;
  count: number;
  images: InspectionImage[];
}


// ======================================================
// LOGIN
// ======================================================

export async function loginOfficer(
  officer_id: string,
  password: string
): Promise<LoginResponse> {

  try {

    const response = await fetch(
      `${API_BASE_URL}/auth/login`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          officer_id,
          password,
        }),
      }
    );

    const data =
      await response.json();

    if (!response.ok) {

      throw new Error(
        data.detail ||
          "Invalid Officer ID or password"
      );
    }

    return data;

  } catch (error: any) {

    console.error(
      "Login API Error:",
      error
    );

    if (error.message) {
      throw error;
    }

    throw new Error(
      "Unable to connect to the server."
    );
  }
}


// ======================================================
// GET ACCESS TOKEN
// ======================================================

export async function getAccessToken(): Promise<
  string | null
> {

  return await SecureStore.getItemAsync(
    "access_token"
  );
}


// ======================================================
// AUTHENTICATED FETCH
// ======================================================

async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
) {

  const token =
    await SecureStore.getItemAsync(
      "access_token"
    );

  if (!token) {

    throw new Error(
      "Authentication token not found."
    );
  }

  const response =
    await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        ...options,

        headers: {
          "Content-Type":
            "application/json",

          ...(options.headers || {}),

          Authorization:
            `Bearer ${token}`,
        },
      }
    );

  return response;
}


// ======================================================
// GET CURRENT OFFICER
// ======================================================

export async function getCurrentOfficer(): Promise<Officer> {

  try {

    const response =
      await authenticatedFetch(
        "/auth/me",
        {
          method: "GET",
        }
      );

    const data =
      await response.json();


    if (response.status === 401) {

      await logoutOfficer();

      throw new Error(
        "Your session has expired. Please login again."
      );
    }


    if (!response.ok) {

      throw new Error(
        data.detail ||
          "Unable to fetch officer information."
      );
    }


    return data;

  } catch (error: any) {

    console.error(
      "Get Current Officer Error:",
      error
    );

    throw error;
  }
}


// ======================================================
// LOGOUT
// ======================================================

export async function logoutOfficer() {

  await SecureStore.deleteItemAsync(
    "access_token"
  );

  await SecureStore.deleteItemAsync(
    "officer_id"
  );

  await SecureStore.deleteItemAsync(
    "role"
  );
}


// ======================================================
// UPLOAD INSPECTION IMAGE
// ======================================================

export async function uploadInspectionImage(
  inspectionId: number,
  imageUri: string,
  imageType: string
): Promise<InspectionImage> {

  const token =
    await SecureStore.getItemAsync(
      "access_token"
    );


  if (!token) {

    throw new Error(
      "Authentication token not found."
    );
  }


  // --------------------------------------------------
  // Filename
  // --------------------------------------------------

  let filename =
    imageUri
      .split("/")
      .pop() ??
    `inspection-${Date.now()}.jpg`;


  // --------------------------------------------------
  // Ensure valid extension
  // --------------------------------------------------

  if (
    !filename
      .toLowerCase()
      .endsWith(".jpg") &&

    !filename
      .toLowerCase()
      .endsWith(".jpeg") &&

    !filename
      .toLowerCase()
      .endsWith(".png") &&

    !filename
      .toLowerCase()
      .endsWith(".webp")
  ) {

    filename =
      `inspection-${Date.now()}.jpg`;
  }


  console.log(
    "================================="
  );

  console.log(
    "Uploading inspection image"
  );

  console.log(
    "Inspection ID:",
    inspectionId
  );

  console.log(
    "Image Type:",
    imageType
  );

  console.log(
    "Image URI:",
    imageUri
  );

  console.log(
    "Filename:",
    filename
  );

  console.log(
    "Platform:",
    Platform.OS
  );

  console.log(
    "================================="
  );


  // ==================================================
  // WEB
  // ==================================================

  if (Platform.OS === "web") {

    try {

      const imageResponse =
        await fetch(imageUri);


      if (!imageResponse.ok) {

        throw new Error(
          "Unable to read the captured image."
        );
      }


      const imageBlob =
        await imageResponse.blob();


      const formData =
        new FormData();


      formData.append(
        "image_type",
        imageType
      );


      formData.append(
        "file",
        imageBlob,
        filename
      );


      const response =
        await fetch(
          `${API_BASE_URL}/inspections/${inspectionId}/images`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },

            body: formData,
          }
        );


      const data =
        await response.json();


      console.log(
        "Upload response:",
        data
      );


      if (!response.ok) {

        throw new Error(
          data.detail ||
            "Image upload failed"
        );
      }


      // Backend response:
      //
      // {
      //   message: "...",
      //   image: {...}
      // }
      //
      // Return only the image object.

      return data.image;

    } catch (error: any) {

      console.error(
        "WEB IMAGE UPLOAD ERROR:",
        error
      );


      throw new Error(
        error?.message ||
          "Unable to upload image."
      );
    }
  }


  // ==================================================
  // ANDROID / IOS
  // ==================================================

  try {

    const uploadResult =
      await FileSystem.uploadAsync(
        `${API_BASE_URL}/inspections/${inspectionId}/images`,

        imageUri,

        {
          fieldName: "file",

          httpMethod: "POST",

          uploadType:
            FileSystem
              .FileSystemUploadType
              .MULTIPART,

          mimeType:
            getMimeType(filename),

          parameters: {
            image_type:
              imageType,
          },

          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );


    console.log(
      "Upload HTTP Status:",
      uploadResult.status
    );


    console.log(
      "Upload Response:",
      uploadResult.body
    );


    // ------------------------------------------------
    // Parse response
    // ------------------------------------------------

    let data: any;


    try {

      data =
        JSON.parse(
          uploadResult.body
        );

    } catch {

      throw new Error(
        "Invalid response received from server."
      );
    }


    // ------------------------------------------------
    // Check status
    // ------------------------------------------------

    if (
      uploadResult.status < 200 ||
      uploadResult.status >= 300
    ) {

      throw new Error(
        data?.detail ||
          "Image upload failed"
      );
    }


    // ------------------------------------------------
    // IMPORTANT
    //
    // FastAPI returns:
    //
    // {
    //   message: "...",
    //   image: {...}
    // }
    //
    // We return data.image.
    // ------------------------------------------------

    if (!data?.image) {

      throw new Error(
        "Image uploaded but server returned an invalid response."
      );
    }


    console.log(
      "Image uploaded successfully:",
      data.image
    );


    return data.image;

  } catch (error: any) {

    console.error(
      "NATIVE IMAGE UPLOAD ERROR:",
      error
    );


    throw new Error(
      error?.message ||
        "Unable to upload inspection image."
    );
  }
}


// ======================================================
// GET INSPECTION IMAGES
// ======================================================

export async function getInspectionImages(
  inspectionId: number
): Promise<InspectionImagesResponse> {

  const token =
    await SecureStore.getItemAsync(
      "access_token"
    );


  if (!token) {

    throw new Error(
      "Authentication token not found."
    );
  }


  const response =
    await fetch(
      `${API_BASE_URL}/inspections/${inspectionId}/images`,
      {
        method: "GET",

        headers: {
          Authorization:
            `Bearer ${token}`,
        },
      }
    );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ||
        "Unable to load inspection images."
    );
  }


  return data;
}


// ======================================================
// MIME TYPE HELPER
// ======================================================

function getMimeType(
  filename: string
): string {

  const extension =
    filename
      .split(".")
      .pop()
      ?.toLowerCase();


  switch (extension) {

    case "png":
      return "image/png";

    case "webp":
      return "image/webp";

    case "jpg":
    case "jpeg":
    default:
      return "image/jpeg";
  }
}


// ======================================================
// CREATE INSPECTION
// ======================================================

export async function createInspection(
  inspectionType:
    | "PHYSICAL"
    | "ECOMMERCE",

  sourceUrl?: string
): Promise<InspectionResponse> {

  const token =
    await SecureStore.getItemAsync(
      "access_token"
    );


  if (!token) {

    throw new Error(
      "Authentication token not found"
    );
  }


  const body: {
    inspection_type:
      | "PHYSICAL"
      | "ECOMMERCE";

    source_url?: string;

  } = {

    inspection_type:
      inspectionType,
  };


  if (
    inspectionType === "ECOMMERCE" &&
    sourceUrl
  ) {

    body.source_url =
      sourceUrl;
  }


  const response =
    await fetch(
      `${API_BASE_URL}/inspections/`,
      {
        method: "POST",

        headers: {

          Authorization:
            `Bearer ${token}`,

          "Content-Type":
            "application/json",
        },

        body:
          JSON.stringify(body),
      }
    );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ||
        "Failed to create inspection"
    );
  }


  return data;
}