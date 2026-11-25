import 'package:flutter/material.dart';

import '../models/pokemon.dart';
import '../services/pokeapi_service.dart';

class PokedexScreen extends StatefulWidget {
  const PokedexScreen({super.key});

  @override
  State<PokedexScreen> createState() => _PokedexScreenState();
}

class _PokedexScreenState extends State<PokedexScreen> {
  final _controlador = TextEditingController();
  Future<Pokemon>? _futuroPokemon;

  void _buscar() {
    final texto = _controlador.text.trim();
    if (texto.isEmpty) return;
    setState(() {
      _futuroPokemon = obtenerPokemon(texto);
    });
  }

  @override
  void dispose() {
    _controlador.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pokédex mínima')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _controlador,
              decoration: const InputDecoration(
                labelText: 'Nombre o número del Pokémon',
                border: OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _buscar(),
            ),
            const SizedBox(height: 12),
            FilledButton(onPressed: _buscar, child: const Text('Buscar')),
            const SizedBox(height: 24),
            Expanded(
              child: _futuroPokemon == null
                  ? const Center(
                      child: Text('Escribe un nombre y presiona Buscar'),
                    )
                  : FutureBuilder<Pokemon>(
                      future: _futuroPokemon,
                      builder: (context, snapshot) {
                        // ✅ TODO 3: tres estados del FutureBuilder.
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(
                            child: CircularProgressIndicator(),
                          );
                        }

                        if (snapshot.hasError) {
                          // Muestra el mensaje de snapshot.error sin el prefijo técnico.
                          final mensaje = snapshot.error
                              .toString()
                              .replaceFirst(RegExp(r'^Exception:\s*'), '');
                          return Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.error_outline,
                                  color: Colors.red,
                                  size: 48,
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  mensaje,
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(
                                    color: Colors.red,
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }

                        if (!snapshot.hasData) {
                          return const Center(child: Text('Sin datos'));
                        }

                        final pokemon = snapshot.data!;
                        return SingleChildScrollView(
                          child: Column(
                            children: [
                              if (pokemon.imagen.isNotEmpty)
                                Image.network(
                                  pokemon.imagen,
                                  height: 190,
                                  errorBuilder: (_, _, _) => const Icon(
                                    Icons.image_not_supported,
                                    size: 90,
                                  ),
                                ),
                              const SizedBox(height: 12),
                              Text(
                                'N.º ${pokemon.id} · ${pokemon.nombre}',
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineSmall
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 10),
                              Wrap(
                                alignment: WrapAlignment.center,
                                spacing: 8,
                                children: [
                                  for (final tipo in pokemon.tipos)
                                    Chip(label: Text(tipo)),
                                ],
                              ),
                              const SizedBox(height: 12),
                              // Reto: altura en metros y peso en kilogramos.
                              Text(
                                'Altura: ${pokemon.altura.toStringAsFixed(1)} m'
                                '   ·   Peso: ${pokemon.peso.toStringAsFixed(1)} kg',
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
