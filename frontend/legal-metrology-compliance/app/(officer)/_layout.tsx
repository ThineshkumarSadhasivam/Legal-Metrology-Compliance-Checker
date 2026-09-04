import { Stack } from "expo-router";

export default function OfficerLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="dashboard" />
      <Stack.Screen name="inspection" />
      <Stack.Screen name="ecommerce" />
      <Stack.Screen name="history" />
      <Stack.Screen name="reports" />
    </Stack>
  );
}