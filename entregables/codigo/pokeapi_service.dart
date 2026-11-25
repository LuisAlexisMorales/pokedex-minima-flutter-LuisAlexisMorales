import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/pokemon.dart';

Future<Pokemon> obtenerPokemon(String nombre) async {
  // ✅ TODO 2: Uri.parse + nombre en minúsculas (y sin espacios).
  final url = Uri.parse(
    'https://pokeapi.co/api/v2/pokemon/${nombre.toLowerCase().trim()}',
  );

  final respuesta = await http.get(url);

  if (respuesta.statusCode == 200) {
    final datos = jsonDecode(respuesta.body) as Map<String, dynamic>;
    return Pokemon.fromJson(datos);
  }

  if (respuesta.statusCode == 404) {
    throw Exception('No se encontró el Pokémon');
  }

  throw Exception('Error al consultar PokéAPI (código ${respuesta.statusCode})');
}
