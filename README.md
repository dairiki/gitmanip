# zipmanip

This is a command line utility that rewrites a zip file. It attempts
to leave the archive contents metadata and ordering as unchanged as
is possible, but recompresses or decompresses the contents.

This was written to use as a git smudge/clean filter to use when using
git to keep a history of zip files. (See below for more on that.)

It may be useful in other cases as well.

## Usage with Git

`Zipmanip` can be used as a clean/smudge filter with `git` so that zip
archives are stored uncompressed in the git index.

(The motivation is that if the zip contents are not compressed, git
should be able to more efficiently pack the deltas between revisions.)

To set this up:

```shell
git config filter.zipmanip.clean "zipmanip --compression-method=store"
git config filter.zipmanip.smudge "zipmanip -9"
# optionally, for diff formatting
git config diff.unzip.textconv "unzip -c -a"
```

Then, edit `.gitattributes` to set the `filter=zipmanip` (and, optionally
`diff=unzip`) on any zip files that you want to store uncompressed.
E.g.

```
*.FCStd binary filter=zipmanip diff=unzip
*.3mf binary filter=zipmanip diff=unzip
*.amf binary filter=zipmanip diff=unzip
```

## Bugs

### On Round-trip Idempotentency

Currently if a zip archive is round tripped — converted to
uncompressed, then recompressed — the result will not be byte-wise
identical to the original. This is due to (at least) a couple of issues.

#### Differing compression algorithm and parameters

It may be possible to improve this situation, at least partially, by
storing information on the original compression type in the
uncompressed archives.

Note that data on compression level may be available from bits 1, 2
and possibly 4 of the ``ZipInfo.flags``.
(See section 4.4.4 of [PKZIP Application Note][AppNote].)

#### Differing use of "zip64" extended header

Also the use of "extended local header" is not preserved. (This
manifests in `.3mf` files written by PrusaSlicer. PrusaSlicer always
writes extended headers.  (This, I think could be fixed with
appropriate use of the `force_zip64` parameters to `ZipFile.open`.)


## Author

Jeff Dairiki <dairiki@dairiki.org>


[AppNote]: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT (PKZIP Application Note)
