import { Stack } from 'expo-router';

export default function AppLayout() {
  return (
    <Stack>
      <Stack.Screen name="home" options={{ title: 'Spaces' }} />
      <Stack.Screen name="space/[id]" options={{ title: 'Space Detail' }} />
      <Stack.Screen name="create-space" options={{ title: 'Create Space' }} />
      <Stack.Screen name="my-spaces" options={{ title: 'My Spaces' }} />
      <Stack.Screen name="profile" options={{ title: 'Profile' }} />
    </Stack>
  );
}
