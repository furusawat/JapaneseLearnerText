<?xml version="1.0" encoding="SHIFT-JIS"?>
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns="http://www.w3.org/1999/xhtml"
	version="1.0">
<xsl:output encoding="Shift_JIS"  method="html"
	doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
	doctype-system="DTD/xhtml1-transitional.dtd"/>

<!-- 作成: 中山智哉 井上義勝 傳智之   -->
<!-- 最終変更: 2002.05.29             -->


<xsl:template match="/">
<html>
<head>
<title>作文コーパス 添削情報表示 <xsl:value-of select="comp/title"/></title>
</head>
<body style="	background-color: #fff1df;
		padding: 1em;
		margin: 0em;
">
<div style="	line-height: 3em;
		padding: 1em 2em;
		background-color: #ffffff;
		margin: 1em;
		border: 1px #484800 solid;">
	<xsl:apply-templates/>

<xsl:if test="//review">
	<ul>
	<xsl:for-each select="//review">
		<li style="color: #ff5599;
		line-height: 2em;
		border-bottom: purple 1px dotted;
		list-style-type: none;">
		<xsl:value-of select="."/>
		</li>
	</xsl:for-each>
	</ul>
</xsl:if>

</div>
<xsl:if test="//note">
	<span style="font-weight: bold; padding:2em;">入力者注</span>
	<dl style="font-size: smaller; padding: 0em 2em; line-height: 1.5em;">
	<xsl:for-each select="//note">
		<dt style="font-weight: bold;  text-decoration: underline;"><xsl:value-of select="."/></dt>
		<dd><xsl:value-of select="@value"/></dd>
	</xsl:for-each>
	</dl>
</xsl:if>
</body>
</html>
</xsl:template>


<!-- 移動元 2002.05.29 -->
<xsl:template match="movefrom">
<span style="padding:0.5em;border:#ff0000 0.1em solid">
	<xsl:apply-templates/>
</span>
<a name="mf{@id}"></a>
<a href="#mt{@id}">
<span style="
	color:#ff0000;
	font-size:smaller;
	position:relative;
	top:-0.5em;
	text-decoration:none;
">[<xsl:value-of select="@id"/>]に移動</span></a>
</xsl:template>


<!-- 移動先 2002.05.29 -->
<xsl:template match="moveto">
<a name="mt{@id}"></a>
<a href="#mf{@id}">
<span style="
	font-size:smaller;
	color:#ff0000;
	position:relative;
	top:-0.5em;
	text-decoration:none;
"> V [<xsl:value-of select="@id"/>]</span></a>
</xsl:template>


<!-- 挿入 2002.05.23 -->
<xsl:template match="put">
  <span style="
	color: #ff0000;
	font-weight: bold;
     ">
     <xsl:apply-templates/>
  <xsl:value-of select="@value"/>
  </span>
</xsl:template>


<!-- 削除 2002.05.23 -->
<xsl:template match="del">
  <span style="
text-decoration: line-through;
  ">
    <xsl:apply-templates/>
  </span>
  <xsl:if test="@comment">
    【<xsl:value-of select="@comment"/>】
  </xsl:if>
</xsl:template>


<!-- 置換 2002.05.23 -->
<xsl:template match="rep">
  <span style="color:#000000; text-decoration:line-through;">
    <xsl:apply-templates/>
  </span>
  <span style="color:#ff0000;
	font-weight: bold;
	position:relative;
	top:1em;
	left:-1em;">
    <xsl:value-of select="@value"/>
  </span>
  <xsl:if test="@comment">
    【<xsl:value-of select="@comment"/>】
  </xsl:if>
</xsl:template>


<!-- より良い表現 -->
<xsl:template match="better">
  <span style="color:black;
	background-color:#ffdddd;
	border:#ffdddd 1px solid;">
    <xsl:apply-templates/>
  </span>
<xsl:value-of select="@comment"/>
  <xsl:if test="@value">
    <span style="color:#0000ff;
	position:relative;
	top:1em;
	left:-1em;">
      <xsl:value-of select="@value"/>
    </span>
  </xsl:if>
</xsl:template>


<!-- 疑わしい表現 2001.12.19 -->
<xsl:template match="doubt">
<span style="
	background-color: #ffdddd;
">
	<xsl:apply-templates/>
</span>
<span style="
	font:bold arial helvetica sans-serif;
	color:#ff0000;
	position:relative;
	top:-0.5em;
"><xsl:choose>
	<xsl:when test="@value [. = '?']">?</xsl:when>
	<xsl:when test="@value [. = '？']">?</xsl:when>
	<xsl:otherwise>? <xsl:value-of select="@value"/></xsl:otherwise>
</xsl:choose></span>
</xsl:template>


<!-- 改行: 段落を変える 2002.05.23 -->
<xsl:template match="newp">
<img src="newp.png" alt="[改行]" title="改行: 段落を変える" style="
	width:1.6em;
	height:1.6em;
	vertical-align:middle;
	margin:1em 0em;
	padding:0em;
	border:0em;
	display: inline;
"/>
</xsl:template>


<!-- 追込: 段落を変えない 2001.12.25 -->
<xsl:template match="runon">
<img src="runon.png" alt="[追込]" title="追込: 段落を変えない" style="
	width:1.2em;
	height:1.2em;
	vertical-align:middle;
	margin:1em 0em;
	padding:0em;
	border:0em;
"/>
</xsl:template>


<!-- 字下げエラー 2001.12.25 -->
<xsl:template match="sperr">
<img src="sperr.png" style="
	width:1.2em;
	height:1.2em;
	vertical-align:middle;
	margin:1em 0em;
	padding:0em;
	border:0em;
">
<xsl:attribute name="alt">[字下げエラー: <xsl:choose>
	<xsl:when test="@value [. = 0] ">空きナシ</xsl:when>
	<xsl:otherwise><xsl:value-of select="@value"/>文字空き</xsl:otherwise>
</xsl:choose>]</xsl:attribute>
<xsl:attribute name="title">字下げエラー: <xsl:choose>
	<xsl:when test="@value [. = 0] ">空きナシ</xsl:when>
	<xsl:otherwise><xsl:value-of select="@value"/>文字空き</xsl:otherwise>
</xsl:choose></xsl:attribute>
</img>
</xsl:template>




<!-- 添削者による注釈 2001.12.25 -->
<xsl:template match="remark">
	<span style="border-bottom: #ff0000 1px dotted;">
		<xsl:apply-templates />
	</span>
  <xsl:if test="@value">
    <span style="color:#ff0000;
		font-size:smaller;
		position:relative;
		top:1em;
		left:-1em;
		border-bottom:#0000ff 1px dotted;">
      <xsl:value-of select="@value"/>
    </span>
  </xsl:if>
</xsl:template>


<!-- 入力者による備考 2002.05.29 -->
<xsl:template match="//note">
<span style="border:1px #484800 solid;
padding: 0em;
margin: 0em 0.3em 0em 0em;
"
title="{@value}">
<xsl:apply-templates/>
</span>
<img src="note.png"
style="
	vertical-align:top;
	margin: 1em 0em;
	padding:0em;
	border:0em;
"
alt="[入力者備考: {@value}]"
title="{@value}"/>
<!--
<xsl:if test="@value">
    <span style="color: #ff0000;
	position:relative;
	top:1em;
	left:-1em;
	font-size:smaller;
	border-bottom:blue 1px dotted;">
      <xsl:value-of select="@value"/>
    </span>
</xsl:if>
-->
</xsl:template>


<!-- 学習者による改行の位置 -->
<xsl:template match="//cp">
	<p/>
</xsl:template>


<!-- 総評 2002.05.29(表示は最上部テンプレートで) -->
<xsl:template match="//review">
</xsl:template>


<xsl:template match="text()">
	<xsl:value-of select="."/>
</xsl:template>


</xsl:stylesheet>
