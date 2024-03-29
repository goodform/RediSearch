from rmtest import BaseModuleTestCase
import redis
import unittest
from hotels import hotels
import random
import time

class SynonymsTestCase(BaseModuleTestCase):

    def testBasicSynonymsUseCase(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child'), 0)

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a boy',
                                            'body', 'this is a test'))

            res = r.execute_command('ft.search', 'idx', 'child', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])

    def testTermOnTwoSynonymsGroup(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child'), 0)
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'offspring'), 1)

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a boy',
                                            'body', 'this is a test'))

            res = r.execute_command('ft.search', 'idx', 'child', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])
            res = r.execute_command('ft.search', 'idx', 'offspring', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])

    def testSynonymGroupWithThreeSynonyms(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a boy',
                                            'body', 'this is a test'))

            res = r.execute_command('ft.search', 'idx', 'child', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])
            res = r.execute_command('ft.search', 'idx', 'offspring', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])

    def testSynonymWithMultipleDocs(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a boy',
                                            'body', 'this is a test'))

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc2', 1.0, 'fields',
                                            'title', 'she is a girl',
                                            'body', 'the child sister'))

            res = r.execute_command('ft.search', 'idx', 'offspring', 'EXPANDER', 'SYNONYM')
            self.assertEqual(res, [int(2), 'doc2', ['title', 'she is a girl', 'body', 'the child sister'], 'doc1', ['title', 'he is a boy', 'body', 'this is a test']])

    def testSynonymUpdate(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)
            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a baby',
                                            'body', 'this is a test'))

            self.assertOk(r.execute_command('ft.synupdate', 'idx', '0', 'baby'))

            self.assertOk(r.execute_command('ft.add', 'idx', 'doc2', 1.0, 'fields',
                                            'title', 'he is another baby',
                                            'body', 'another test'))

            res = r.execute_command('ft.search', 'idx', 'child', 'EXPANDER', 'SYNONYM')
            # synonyms are applied from the moment they were added, previuse docs are not reindexed
            self.assertEqual(res, [int(1), 'doc2', ['title', 'he is another baby', 'body', 'another test']])

    def testSynonymDump(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'baby', 'child'), 1)
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'tree', 'wood'), 2)
            self.assertEqual(r.execute_command('ft.syndump', 'idx'), ['baby', [int(1)], 'offspring', [int(0)], 'wood', [int(2)], 'tree', [int(2)], 'child', [int(0), int(1)], 'boy', [int(0)]])

    def testSynonymAddWrongArity(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            exceptionStr = None
            try:
                r.execute_command('ft.synadd', 'idx')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'wrong number of arguments for \'ft.synadd\' command')

    def testSynonymAddUnknownIndex(self):
        with self.redis() as r:
            r.flushdb()
            exceptionStr = None
            try:
                r.execute_command('ft.synadd', 'idx', 'boy', 'child')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'unknown index name')

    def testSynonymUpdateWrongArity(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            r.execute_command('ft.synadd', 'idx', 'boy', 'child')
            exceptionStr = None
            try:
                r.execute_command('ft.synupdate', 'idx', '0')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'wrong number of arguments for \'ft.synupdate\' command')

    def testSynonymUpdateUnknownIndex(self):
        with self.redis() as r:
            r.flushdb()
            exceptionStr = None
            try:
                r.execute_command('ft.synupdate', 'idx', '0', 'child')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'unknown index name')

    def testSynonymUpdateNotNumberId(self):
        with self.redis() as r:
            r.flushdb()
            exceptionStr = None
            try:
                r.execute_command('ft.synupdate', 'idx', 'test', 'child')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'wrong parameters, id is not an integer')

    def testSynonymUpdateOutOfRangeId(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            r.execute_command('ft.synadd', 'idx', 'boy', 'child')
            exceptionStr = None
            try:
                r.execute_command('ft.synupdate', 'idx', '1', 'child')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'given id does not exists')

    def testSynonymDumpWrongArity(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            r.execute_command('ft.synadd', 'idx', 'boy', 'child')
            exceptionStr = None
            try:
                r.execute_command('ft.syndump')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'wrong number of arguments for \'ft.syndump\' command')

    def testSynonymUnknownIndex(self):
        with self.redis() as r:
            r.flushdb()
            exceptionStr = None
            try:
                r.execute_command('ft.syndump', 'idx')
            except Exception as e:
                exceptionStr = str(e).lower()
            self.assertEqual(exceptionStr, 'unknown index name')

    def testSynonymsRdb(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)
            for _ in self.client.retry_with_rdb_reload():
                self.assertEqual(r.execute_command('ft.syndump', 'idx'), ['offspring', [int(0)], 'child', [int(0)], 'boy', [int(0)]])

    def testTwoSynonymsSearch(self):
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy', 'child', 'offspring'), 0)
            self.assertOk(r.execute_command('ft.add', 'idx', 'doc1', 1.0, 'fields',
                                            'title', 'he is a boy child boy',
                                            'body', 'another test'))

            res = r.execute_command('ft.search', 'idx', 'offspring offspring', 'EXPANDER', 'SYNONYM')
            # synonyms are applied from the moment they were added, previuse docs are not reindexed
            self.assertEqual(res, [int(1), 'doc1', ['title', 'he is a boy child boy', 'body', 'another test']])

    def testSynonymsIntensiveLoad(self):
        iterations = 1000
        with self.redis() as r:
            r.flushdb()
            self.assertOk(r.execute_command(
                'ft.create', 'idx', 'schema', 'title', 'text', 'body', 'text'))
            for i in list(range(iterations)):
                self.assertEqual(r.execute_command('ft.synadd', 'idx', 'boy%d' % i, 'child%d' % i, 'offspring%d' % i), i)
            for i in list(range(iterations)):
                self.assertOk(r.execute_command('ft.add', 'idx', 'doc%d' % i, 1.0, 'fields',
                                                'title', 'he is a boy%d' % i,
                                                'body', 'this is a test'))
            for _ in self.client.retry_with_rdb_reload():
                for i in list(range(iterations)):
                    res = r.execute_command('ft.search', 'idx', 'child%d' % i, 'EXPANDER', 'SYNONYM')
                    self.assertEqual(res, [int(1), 'doc%d' % i, ['title', 'he is a boy%d' % i, 'body', 'this is a test']])
