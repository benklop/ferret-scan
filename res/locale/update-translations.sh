#/bin/sh
xgettext --language=Python \
	--copyright-holder='bq' \
	--package-name=Ferret Scan \
	--package-version=0.2 \
	--msgid-bugs-address=jesus.arroyo@bq.com \
	--keyword=_ \
	--output=ferret.pot \
	--from-code=UTF-8 \
	`find ../../src/ferret -name "*.py"`

for LANG in `ls .`; do
	if [ -e $LANG/LC_MESSAGES/ferret.po ]; then
		msgmerge -U $LANG/LC_MESSAGES/ferret.po ferret.pot
		msgfmt $LANG/LC_MESSAGES/ferret.po --output-file $LANG/LC_MESSAGES/ferret.mo
	fi
done
