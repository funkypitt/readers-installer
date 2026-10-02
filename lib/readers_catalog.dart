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
//
// The catalogue also names the desktop version of an app, when there is one
// ("desktop": application id → GitHub page and systems); the app's page shows
// it as a link opened in the browser.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart' show ValueNotifier;
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:obtainium/core/logging/app_logger.dart';
import 'package:obtainium/providers/apps_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String readersCatalogUrl =
    'https://raw.githubusercontent.com/funkypitt/readers-installer/main/assets/catalog.json';
const String _offeredKey = 'readersCatalogOffered';
const String _formerSourcePrefix = 'https://github.com/funkypitt/';

/// The desktop version of an app of the catalogue.
class DesktopVersion {
  final String url;
  final String systems;
  const DesktopVersion(this.url, this.systems);
}

/// Desktop versions by application id, filled from the catalogue at start.
final ValueNotifier<Map<String, DesktopVersion>> readersDesktop = ValueNotifier(
  const {},
);

void _readDesktop(String json) {
  try {
    final desktop = (jsonDecode(json) as Map<String, dynamic>)['desktop'];
    if (desktop is! Map) return;
    final found = <String, DesktopVersion>{};
    desktop.forEach((id, value) {
      if (id is! String || value is! Map) return;
      final url = value['url'];
      final systems = value['systems'];
      if (url is String && url.startsWith('https://')) {
        found[id] = DesktopVersion(url, systems is String ? systems : '');
      }
    });
    readersDesktop.value = found;
  } catch (e) {
    AppLogger.info('Catalogue: desktop versions not read ($e)');
  }
}

/// Adds the Reader's apps that were never offered on this device to the list
/// of tracked apps, then looks up their latest versions.
Future<void> syncReadersCatalog(AppsProvider apps) async {
  try {
    final bundled = await rootBundle.loadString('assets/catalog.json');
    _readDesktop(bundled);
    await apps.waitForAppsToLoad();
    await _merge(apps, bundled);
  } catch (e, stack) {
    AppLogger.error(e, stackTrace: stack, message: 'Catalogue: bundled list');
  }
  try {
    final response = await http
        .get(Uri.parse(readersCatalogUrl))
        .timeout(const Duration(seconds: 15));
    if (response.statusCode == 200) {
      final online = utf8.decode(response.bodyBytes);
      _readDesktop(online);
      await _merge(apps, online);
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
