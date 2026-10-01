// Reader's Installer and Updater: the catalogue of the Reader's apps.
//
// Not part of Obtainium. The apps this fork exists to install are listed in
// assets/catalog.json (shipped with the app) and in the same file on the
// project's main branch (read at start, so an app published later appears
// without waiting for a new version of the installer). Each app is offered
// once: one the user removed from the list is not added again.
//
// The catalogue points at the personal F-Droid repository (one index file on
// GitHub Pages) rather than at each app's GitHub releases: GitHub's API allows
// 60 anonymous requests an hour per address, which sixteen apps use up in one
// sitting ("too many requests"). Entries that version 1.0.0 created on GitHub
// are moved to the repository the first time this version starts.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:obtainium/core/logging/app_logger.dart';
import 'package:obtainium/providers/apps_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String readersCatalogUrl =
    'https://raw.githubusercontent.com/funkypitt/readers-installer/main/assets/catalog.json';
const String _offeredKey = 'readersCatalogOffered';
const String _formerSourcePrefix = 'https://github.com/funkypitt/';

/// Adds the Reader's apps that were never offered on this device to the list
/// of tracked apps, then looks up their latest versions.
Future<void> syncReadersCatalog(AppsProvider apps) async {
  try {
    await apps.waitForAppsToLoad();
    await _merge(apps, await rootBundle.loadString('assets/catalog.json'));
  } catch (e, stack) {
    AppLogger.error(e, stackTrace: stack, message: 'Catalogue: bundled list');
  }
  try {
    final response = await http
        .get(Uri.parse(readersCatalogUrl))
        .timeout(const Duration(seconds: 15));
    if (response.statusCode == 200) {
      await _merge(apps, utf8.decode(response.bodyBytes));
    }
  } catch (e) {
    // Offline, or GitHub unreachable: the bundled list has been applied.
    AppLogger.info('Catalogue: online list not read ($e)');
  }
}

Future<void> _merge(AppsProvider apps, String json) async {
  final prefs = await SharedPreferences.getInstance();
  final offered = (prefs.getStringList(_offeredKey) ?? <String>[]).toSet();
  final entries = ((jsonDecode(json) as Map<String, dynamic>)['apps'] as List)
      .cast<Map<String, dynamic>>();
  final fresh = entries
      .where((e) {
        final existing = apps.apps[e['id']];
        if (existing == null) return !offered.contains(e['id']);
        // tracked on GitHub by version 1.0.0: move it to the catalogue's source
        return existing.app.url != e['url'] &&
            existing.app.url.startsWith(_formerSourcePrefix);
      })
      .toList();
  if (fresh.isNotEmpty) {
    await apps.import(jsonEncode(<String, dynamic>{'apps': fresh}));
  }
  offered.addAll(entries.map((e) => e['id'] as String));
  await prefs.setStringList(_offeredKey, offered.toList());
  if (fresh.isNotEmpty) {
    unawaited(
      apps
          .checkUpdates(
            specificIds: fresh.map((e) => e['id'] as String).toList(),
          )
          .then((_) {}, onError: (Object e) {
            AppLogger.info('Catalogue: first version check failed ($e)');
          }),
    );
  }
}
