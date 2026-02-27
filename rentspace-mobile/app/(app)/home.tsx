import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { router } from 'expo-router';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>All Spaces</Text>

      <TouchableOpacity onPress={() => router.push('/create-space')}>
        <Text style={styles.link}>Create Space</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/my-spaces')}>
        <Text style={styles.link}>My Spaces</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/profile')}>
        <Text style={styles.link}>Profile</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  link: { marginVertical: 10, fontSize: 16, color: 'blue' },
});
