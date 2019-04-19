#!/bin/bash
#################################
# Speech Script by Dan Fountain #
#      TalkToDanF@gmail.com     #
#################################
# http://archive.is/OgeSS

 
INPUT=$*
STRINGNUM=0
 
ary=($INPUT)
echo "---------------------------"
echo "Speech Script by Dan Fountain"
echo "TalkToDanF@gmail.com"
echo "---------------------------"
for key in "${!ary[@]}" 
  do
    SHORTTMP[$STRINGNUM]="${SHORTTMP[$STRINGNUM]} ${ary[$key]}"
    LENGTH=$(echo ${#SHORTTMP[$STRINGNUM]})
    #echo "word:$key, ${ary[$key]}"
    #echo "adding to: $STRINGNUM"
    if [[ "$LENGTH" -lt "100" ]]; then
      #echo starting new line
      SHORT[$STRINGNUM]=${SHORTTMP[$STRINGNUM]}
    else
      STRINGNUM=$(($STRINGNUM+1))
      SHORTTMP[$STRINGNUM]="${ary[$key]}"
      SHORT[$STRINGNUM]="${ary[$key]}"
    fi
done
 
for key in "${!SHORT[@]}"
  do
    #echo "line: $key is: ${SHORT[$key]}"
 
    echo "Playing line: $(($key+1)) of $(($STRINGNUM+1))"
    NEXTURL=$(echo ${SHORT[$key]} | xxd -plain | tr -d '\n' | sed 's/\(..\)/%\1/g')
    mpg123 -q "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$NEXTURL&tl=De-de"
done
