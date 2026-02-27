import { View, Text, StyleSheet } from 'react-native';

export default function MySpacesScreen() {
  return (
    <View style={styles.container}>
      <Text>My Spaces</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
});
