class Pokemon {
  final int id;
  final String nombre;
  final String imagen;
  final List<String> tipos;

  // Reto: PokéAPI da height en decímetros y weight en hectogramos.
  final double altura; // metros
  final double peso; // kilogramos

  Pokemon({
    required this.id,
    required this.nombre,
    required this.imagen,
    required this.tipos,
    this.altura = 0.0,
    this.peso = 0.0,
  });

  factory Pokemon.fromJson(Map<String, dynamic> json) {
    // ✅ TODO 1: los cuatro atributos se leen directamente del JSON.
    return Pokemon(
      id: json['id'] as int,
      nombre: json['name'] as String,
      imagen:
          json['sprites']['other']['official-artwork']['front_default'] ?? '',
      tipos: [for (final t in json['types']) t['type']['name'] as String],
      // Reto: convertir decímetros a metros y hectogramos a kilogramos.
      altura: ((json['height'] as num?) ?? 0) / 10,
      peso: ((json['weight'] as num?) ?? 0) / 10,
    );
  }
}
