import { View, Text, StyleSheet } from 'react-native';

export default function CreateSpaceScreen() {
  return (
    <View style={styles.container}>
      <Text>Create Space Form</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
});
